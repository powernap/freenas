import asyncio
import os
import time
import subprocess as su

import iocage_lib.iocage as ioc
import libzfs
import requests
import itertools
import pathlib
import json
import sqlite3
from iocage_lib.ioc_check import IOCCheck
from iocage_lib.ioc_clean import IOCClean
from iocage_lib.ioc_fetch import IOCFetch
from iocage_lib.ioc_image import IOCImage
from iocage_lib.ioc_json import IOCJson
# iocage's imports are per command, these are just general facilities
from iocage_lib.ioc_list import IOCList
from iocage_lib.ioc_upgrade import IOCUpgrade

from middlewared.client import ClientException
from middlewared.schema import Bool, Dict, Int, List, Str, accepts
from middlewared.service import CRUDService, job, private
from middlewared.service_exception import CallError, ValidationErrors
from middlewared.utils import filter_list
from middlewared.validators import IpInUse, ShouldBe


SHUTDOWN_LOCK = asyncio.Lock()


class JailService(CRUDService):

    class Config:
        process_pool = True

    # FIXME: foreign schemas cannot be referenced when
    # using `process_pool`
    # @filterable
    @accepts(
        List('query-filters'),
        Dict('query-options', additional_attrs=True),
    )
    def query(self, filters=None, options=None):
        options = options or {}
        jail_identifier = None
        jails = []

        if filters and len(filters) == 1 and list(
                filters[0][:2]) == ['host_hostuuid', '=']:
            jail_identifier = filters[0][2]

        recursive = False if jail_identifier == 'default' else True

        try:
            jail_dicts = ioc.IOCage(
                jail=jail_identifier).get('all', recursive=recursive)

            if jail_identifier == 'default':
                jail_dicts['host_hostuuid'] = 'default'
                jails.append(jail_dicts)
            else:
                for jail in jail_dicts:
                    jail = list(jail.values())[0]
                    jail['id'] = jail['host_hostuuid']
                    if jail['dhcp'] == 'on':
                        uuid = jail['host_hostuuid']

                        if jail['state'] == 'up':
                            interface = jail['interfaces'].split(',')[0].split(
                                ':')[0]
                            if interface == 'vnet0':
                                # Inside jails they are epair0b
                                interface = 'epair0b'
                            ip4_cmd = ['jexec', f'ioc-{uuid}', 'ifconfig',
                                       interface, 'inet']
                            out = su.check_output(ip4_cmd)
                            jail['ip4_addr'] = f'{interface}|' \
                                f'{out.splitlines()[2].split()[1].decode()}'
                        else:
                            jail['ip4_address'] = 'DHCP (not running)'
                    jails.append(jail)
        except BaseException:
            # Brandon is working on fixing this generic except, till then I
            # am not going to make the perfect the enemy of the good enough!
            self.logger.debug('iocage failed to fetch jails', exc_info=True)
            pass

        return filter_list(jails, filters, options)
    query._fiterable = True

    @accepts(
        Dict(
            "options",
            Str("release", required=True),
            Str("template"),
            Str("pkglist"),
            Str("uuid", required=True),
            Bool("basejail", default=False),
            Bool("empty", default=False),
            Bool("short", default=False),
            List("props", default=[])
        )
    )
    async def do_create(self, options):
        """Creates a jail."""
        # Typically one would return the created jail's id in this
        # create call BUT since jail creation may or may not involve
        # fetching a release, which in turn could be time consuming
        # and could then block for a long time. This dictates that we
        # make it a job, but that violates the principle that CRUD methods
        # are not jobs as yet, so I settle on making this a wrapper around
        # the main job that calls this and return said job's id instead of
        # the created jail's id

        return await self.middleware.call('jail.create_job', options)

    @private
    @job()
    def create_job(self, job, options):
        verrors = ValidationErrors()

        try:
            self.check_jail_existence(options['uuid'], skip=False)

            verrors.add(
                'uuid',
                f'A jail with uuid {options["uuid"]} already exists'
            )
            raise verrors
        except CallError:
            # A jail does not exist with the provided uuid, we can create one now

            self.validate_ips(verrors, options)
            job.set_progress(20, 'Initial validation complete')

            iocage = ioc.IOCage(skip_jails=True)

        release = options["release"]
        template = options.get("template", False)
        pkglist = options.get("pkglist", None)
        uuid = options["uuid"]
        basejail = options["basejail"]
        empty = options["empty"]
        short = options["short"]
        props = options["props"]
        pool = IOCJson().json_get_value("pool")
        iocroot = IOCJson(pool).json_get_value("iocroot")

        if template:
            release = template

        if (
                not os.path.isdir(f'{iocroot}/releases/{release}') and
                not template and
                not empty
        ):
            self.middleware.call_sync(
                'jail.fetch', {"release": release}, job=True
            )

        err, msg = iocage.create(
            release,
            props,
            0,
            pkglist,
            template=template,
            short=short,
            _uuid=uuid,
            basejail=basejail,
            empty=empty
        )

        if err:
            raise CallError(msg)

        return True

    @private
    def validate_ips(self, verrors, options, schema='options.props', exclude=None):
        for item in options['props']:
            for f in ('ip4_addr', 'ip6_addr'):
                if f in item:
                    for ip in item.split('=')[1].split(','):
                        try:
                            IpInUse(self.middleware, exclude)(ip.split('|')[1].split('/')[0])
                        except ShouldBe as e:
                            verrors.add(
                                f'{schema}.{f}',
                                str(e)
                            )

        if verrors:
            raise verrors

    @accepts(Str("jail"), Dict(
             "options",
             Bool("plugin", default=False),
             additional_attrs=True,
             ))
    def do_update(self, jail, options):
        """Sets a jail property."""
        plugin = options.pop("plugin")
        _, _, iocage = self.check_jail_existence(jail)

        name = options.pop("name", None)

        verrors = ValidationErrors()

        jail = self.query([['id', '=', jail]], {'get': True})

        exclude_ips = [
            ip.split('|')[1].split('/')[0]
            for f in ('ip4_addr', 'ip6_addr') for ip in jail[f].split(',')
            if ip != 'none'
        ]

        self.validate_ips(
            verrors, {'props': [f'{k}={v}' for k, v in options.items()]},
            'options', exclude_ips
        )

        for prop, val in options.items():
            p = f"{prop}={val}"

            try:
                iocage.set(p, plugin)
            except RuntimeError as err:
                raise CallError(err)

        if name:
            iocage.rename(name)

        return True

    @accepts(Str("jail"))
    def do_delete(self, jail):
        """Takes a jail and destroys it."""
        _, _, iocage = self.check_jail_existence(jail)

        # TODO: Port children checking, release destroying.
        iocage.destroy_jail()

        return True

    @private
    def check_dataset_existence(self):
        IOCCheck()

    @private
    def check_jail_existence(self, jail, skip=True):
        """Wrapper for iocage's API, as a few commands aren't ported to it"""
        try:
            iocage = ioc.IOCage(skip_jails=skip, jail=jail)
            jail, path = iocage.__check_jail_existence__()
        except (SystemExit, RuntimeError):
            raise CallError(f"jail '{jail}' not found!")

        return jail, path, iocage

    @accepts()
    def get_activated_pool(self):
        """Returns the activated pool if there is one, or None"""
        try:
            pool = ioc.IOCage(skip_jails=True).get("", pool=True)
        except Exception:
            pool = None

        return pool

    @accepts(
        Dict(
            "options",
            Str("release"),
            Str("server", default="download.freebsd.org"),
            Str("user", default="anonymous"),
            Str("password", default="anonymous@"),
            Str("name", default=None),
            Bool("accept", default=True),
            List("props"),
            List(
                "files",
                default=["MANIFEST", "base.txz", "lib32.txz", "doc.txz"]
            ),
            Str("branch", default=None)
        )
    )
    @job(lock=lambda args: f"jail_fetch:{args[-1]}")
    def fetch(self, job, options):
        """Fetches a release or plugin."""
        fetch_output = {'error': False, 'install_notes': []}

        verrors = ValidationErrors()

        self.validate_ips(verrors, options)

        def progress_callback(content):
            level = content['level']
            msg = content['message'].strip('\n')

            if job.progress['percent'] == 90:
                for split_msg in msg.split('\n'):
                    fetch_output['install_notes'].append(split_msg)

            if level == 'EXCEPTION':
                fetch_output['error'] = True
                raise CallError(msg)

            job.set_progress(None, msg)

            if '  These pkgs will be installed:' in msg:
                job.set_progress(50, msg)
            elif 'Installing plugin packages:' in msg:
                job.set_progress(75, msg)
            elif 'Command output:' in msg:
                job.set_progress(90, msg)

        self.check_dataset_existence()  # Make sure our datasets exist.
        start_msg = None
        finaL_msg = None

        if options["name"] is not None:
            options["plugin_file"] = True
            start_msg = 'Starting plugin install'
            finaL_msg = f"Plugin: {options['name']} installed"

        options["accept"] = True

        iocage = ioc.IOCage(callback=progress_callback, silent=False)

        job.set_progress(0, start_msg)
        iocage.fetch(**options)

        if options['name'] is not None:
            # This is to get the admin URL and such
            fetch_output['install_notes'] += job.progress['description'].split(
                '\n')

        job.set_progress(100, finaL_msg)

        return fetch_output

    @accepts(Str("resource", enum=["RELEASE", "TEMPLATE", "PLUGIN"]),
             Bool("remote", default=False))
    def list_resource(self, resource, remote):
        """Returns a JSON list of the supplied resource on the host"""
        self.check_dataset_existence()  # Make sure our datasets exist.
        iocage = ioc.IOCage(skip_jails=True)
        resource = "base" if resource == "RELEASE" else resource.lower()

        if resource == "plugin":
            if remote:
                try:
                    resource_list = self.middleware.call_sync(
                        'cache.get', 'iocage_remote_plugins')

                    return resource_list
                except ClientException as e:
                    # The jail plugin runs in another process, it's seen as
                    # a client
                    if e.trace and e.trace['class'] == 'KeyError':
                        pass  # It's either new or past cache date
                    else:
                        raise

                resource_list = iocage.fetch(list=True, plugins=True,
                                             header=False)
            else:
                resource_list = iocage.list("all", plugin=True)
                pool = IOCJson().json_get_value("pool")
                iocroot = IOCJson(pool).json_get_value("iocroot")
                index_path = f'{iocroot}/.plugin_index/INDEX'

                if not pathlib.Path(index_path).is_file():
                    index_json = None
                    raise CallError(
                        'Plugin INDEX doesn\'t exist, unable to list pkg'
                        ' versions for any plugins.')
                else:
                    index_fd = open(index_path, 'r')
                    index_json = json.load(index_fd)

            for plugin in resource_list:
                for i, elem in enumerate(plugin):
                    # iocage returns - for None
                    plugin[i] = elem if elem != "-" else None

                if remote:
                    pv = self.get_plugin_version(plugin[2])
                else:
                    pv = self.get_local_plugin_version(
                        plugin[1], index_json, iocroot)

                resource_list[resource_list.index(plugin)] = plugin + pv

            if remote:
                self.middleware.call_sync(
                    'cache.put', 'iocage_remote_plugins', resource_list,
                    86400
                )
            else:
                index_fd.close()
        elif resource == "base":
            try:
                if remote:
                    resource_list = self.middleware.call_sync(
                        'cache.get', 'iocage_remote_releases')

                    return resource_list
            except ClientException as e:
                # The jail plugin runs in another process, it's seen as
                # a client
                if e.trace and e.trace['class'] == 'KeyError':
                    pass  # It's either new or past cache date
                else:
                    raise

            resource_list = iocage.fetch(list=True, remote=remote, http=True)

            if remote:
                self.middleware.call_sync(
                    'cache.put', 'iocage_remote_releases', resource_list,
                    86400
                )
        else:
            resource_list = iocage.list(resource)

        return resource_list

    @accepts(Str("action", enum=["START", "STOP", "RESTART"]))
    def rc_action(self, action):
        """Does specified action on rc enabled (boot=on) jails"""
        iocage = ioc.IOCage(rc=True)

        if action == "START":
            iocage.start()
        elif action == "STOP":
            iocage.stop()
        else:
            iocage.stop()
            time.sleep(0.5)
            iocage.start()

        return True

    @accepts(Str("jail"))
    def start(self, jail):
        """Takes a jail and starts it."""
        _, _, iocage = self.check_jail_existence(jail)

        iocage.start()

        return True

    @accepts(Str("jail"))
    def stop(self, jail):
        """Takes a jail and stops it."""
        _, _, iocage = self.check_jail_existence(jail)

        iocage.stop()

        return True

    @private
    def get_iocroot(self):
        pool = IOCJson().json_get_value("pool")
        return IOCJson(pool).json_get_value("iocroot")

    @accepts(
        Str("jail"),
        Dict(
            "options",
            Str("action", enum=["ADD", "EDIT", "REMOVE", "REPLACE", "LIST"], required=True),
            Str("source"),
            Str("destination"),
            Str("fstype"),
            Str("fsoptions"),
            Str("dump"),
            Str("pass"),
            Int("index", default=None),
        ))
    def fstab(self, jail, options):
        """Adds an fstab mount to the jail"""
        uuid, _, iocage = self.check_jail_existence(jail, skip=False)
        status, jid = IOCList.list_get_jid(uuid)

        if status:
            raise CallError(
                f'{jail} should not be running when adding a mountpoint')

        verrors = ValidationErrors()

        action = options['action'].lower()
        source = options.get('source')
        if source:
            if not os.path.exists(source):
                verrors.add(
                    'source',
                    'Provided path for source does not exist'
                )

            source = source.replace(' ', r'\040')  # fstab hates spaces ;)

        destination = options.get('destination')
        if destination:
            destination = f'/{destination}' if destination[0] != '/' else destination
            dst = f'{self.get_iocroot()}/jails/{jail}/root{destination}'
            if 'mnt' in destination:
                verrors.add(
                    'destination',
                    'Destination should not include the jail path. '
                    'e.g "/mnt/iocage/jails/btsync/root/" Path should be specified'
                    'after /'
                )
            elif os.path.exists(dst):
                if not os.path.isdir(dst):
                    verrors.add(
                        'destination',
                        'Destination is not a directory, please provide a valid destination'
                    )
                elif os.listdir(dst):
                    verrors.add(
                        'destination',
                        'Destination directory should be empty'
                    )

            # fstab hates spaces ;)
            destination = destination.replace(' ', r'\040')

        if action != 'list':
            for f in options:
                if not options.get(f) and f not in ('index',):
                    verrors.add(
                        f,
                        'This field is required'
                    )

        fstype = options.get('fstype')
        fsoptions = options.get('fsoptions')
        dump = options.get('dump')
        _pass = options.get('pass')
        index = options.get('index')

        if verrors:
            raise verrors

        if action == 'replace' and index is None:
            raise ValueError(
                "Index must not be None when replacing fstab entry"
            )

        _list = iocage.fstab(action, source, destination, fstype, fsoptions,
                             dump, _pass, index=index, add_path=True)

        if action == "list":
            split_list = {}
            for i in _list:
                split_list[i[0]] = i[1].split()

            return split_list

        return True

    @accepts(Str("pool"))
    def activate(self, pool):
        """Activates a pool for iocage usage, and deactivates the rest."""
        zfs = libzfs.ZFS(history=True, history_prefix="<iocage>")
        pools = zfs.pools
        prop = "org.freebsd.ioc:active"

        for _pool in pools:
            if _pool.name == pool:
                ds = zfs.get_dataset(_pool.name)
                ds.properties[prop] = libzfs.ZFSUserProperty("yes")
            else:
                ds = zfs.get_dataset(_pool.name)
                ds.properties[prop] = libzfs.ZFSUserProperty("no")

        return True

    @accepts(Str("ds_type", enum=["ALL", "JAIL", "TEMPLATE", "RELEASE"]))
    def clean(self, ds_type):
        """Cleans all iocage datasets of ds_type"""

        if ds_type == "JAIL":
            IOCClean().clean_jails()
        elif ds_type == "ALL":
            IOCClean().clean_all()
        elif ds_type == "TEMPLATE":
            IOCClean().clean_templates()

        return True

    @accepts(
        Str("jail"),
        List("command"),
        Dict("options", Str("host_user", default="root"), Str("jail_user")))
    def exec(self, jail, command, options):
        """Issues a command inside a jail."""
        _, _, iocage = self.check_jail_existence(jail, skip=False)

        host_user = options["host_user"]
        jail_user = options.get("jail_user", None)

        if isinstance(command[0], list):
            # iocage wants a flat list, not a list inside a list
            command = list(itertools.chain.from_iterable(command))

        # We may be getting ';', '&&' and so forth. Adding the shell for
        # safety.
        if len(command) == 1:
            command = ["/bin/sh", "-c"] + command

        host_user = "" if jail_user and host_user == "root" else host_user
        msg = iocage.exec(command, host_user, jail_user, msg_return=True)

        return msg.decode("utf-8")

    @accepts(Str("jail"))
    @job(lock=lambda args: f"jail_update:{args[-1]}")
    def update_to_latest_patch(self, job, jail):
        """Updates specified jail to latest patch level."""

        uuid, path, _ = self.check_jail_existence(jail)
        status, jid = IOCList.list_get_jid(uuid)
        conf = IOCJson(path).json_load()

        # Sometimes if they don't have an existing patch level, this
        # becomes 11.1 instead of 11.1-RELEASE
        _release = conf["release"].rsplit("-", 1)[0]
        release = _release if "-RELEASE" in _release else conf["release"]

        started = False

        if conf["type"] == "jail":
            if not status:
                self.start(jail)
                started = True
        else:
            return False

        if conf["basejail"] != "yes":
            IOCFetch(release).fetch_update(True, uuid)
        else:
            # Basejails only need their base RELEASE updated
            IOCFetch(release).fetch_update()

        if started:
            self.stop(jail)

        return True

    @accepts(Str("jail"), Str("release"))
    @job(lock=lambda args: f"jail_upgrade:{args[-1]}")
    def upgrade(self, job, jail, release):
        """Upgrades specified jail to specified RELEASE."""

        uuid, path, _ = self.check_jail_existence(jail)
        status, jid = IOCList.list_get_jid(uuid)
        conf = IOCJson(path).json_load()
        root_path = f"{path}/root"
        started = False

        if conf["type"] == "jail":
            if not status:
                self.start(jail)
                started = True
        else:
            return False

        IOCUpgrade(conf, release, root_path).upgrade_jail()

        if started:
            self.stop(jail)

        return True

    @accepts(Str("jail"))
    @job(lock=lambda args: f"jail_export:{args[-1]}")
    def export(self, job, jail):
        """Exports jail to zip file"""
        uuid, path, _ = self.check_jail_existence(jail)
        status, jid = IOCList.list_get_jid(uuid)
        started = False

        if status:
            self.stop(jail)
            started = True

        IOCImage().export_jail(uuid, path)

        if started:
            self.start(jail)

        return True

    @accepts(Str("jail"))
    @job(lock=lambda args: f"jail_import:{args[-1]}")
    def _import(self, job, jail):
        """Imports jail from zip file"""

        IOCImage().import_jail(jail)

        return True

    @private
    def get_plugin_version(self, pkg):
        """
        Fetches a list of pkg's from the http://pkg.cdn.trueos.org/iocage/
        repo and returns a list with the pkg version and plugin revision
        """
        try:
            pkg_dict = self.middleware.call_sync('cache.get', 'iocage_rpkgdict')
            r_plugins = self.middleware.call_sync('cache.get',
                                                  'iocage_rplugins')
        except ClientException as e:
            # The jail plugin runs in another process, it's seen as a client
            if e.trace and e.trace['class'] == 'KeyError':
                r_pkgs = requests.get('http://pkg.cdn.trueos.org/iocage/All')
                r_pkgs.raise_for_status()
                pkg_dict = {}
                for i in r_pkgs.iter_lines():
                    i = i.decode().split('"')

                    try:
                        pkg, version = i[1].rsplit('-', 1)
                        pkg_dict[pkg] = version
                    except (ValueError, IndexError):
                        continue  # It's not a pkg
                self.middleware.call_sync(
                    'cache.put', 'iocage_rpkgdict', pkg_dict,
                    86400
                )

                r_plugins = requests.get(
                    'https://raw.githubusercontent.com/freenas/'
                    'iocage-ix-plugins/master/INDEX'
                )
                r_plugins.raise_for_status()

                r_plugins = r_plugins.json()
                self.middleware.call_sync(
                    'cache.put', 'iocage_rplugins', r_plugins,
                    86400
                )
            else:
                raise

        if pkg == 'bru-server':
            return ['N/A', '1']
        elif pkg == 'sickrage':
            return ['Git branch - master', '1']

        try:
            primary_pkg = r_plugins[pkg]['primary_pkg'].split('/', 1)[-1]

            version = pkg_dict[primary_pkg]
            version = [version.rsplit('%2', 1)[0].replace('.txz', ''), '1']
        except KeyError:
            version = ['N/A', 'N/A']

        return version

    @private
    def get_local_plugin_version(self, plugin, index_json, iocroot):
        """
        Checks the primary_pkg key in the INDEX with the pkg version
        inside the jail.
        """
        if index_json is None:
            return ['N/A', 'N/A']

        try:
            base_plugin = plugin.rsplit('_', 1)[0]  # May have multiple
            primary_pkg = index_json[base_plugin]['primary_pkg']
            version = ['N/A', 'N/A']

            # Since these are plugins, we don't want to spin them up just to
            # check a pkg, directly accessing the db is best in this case.
            db_rows = self.read_plugin_pkg_db(
                f'{iocroot}/jails/{plugin}/root/var/db/pkg/local.sqlite',
                primary_pkg)

            for row in db_rows:
                if primary_pkg == row[1] or primary_pkg == row[2]:
                    version = [row[3], '1']
                    break
        except KeyError:
            version = ['N/A', 'N/A']

        return version

    @private
    def read_plugin_pkg_db(self, db, pkg):
        try:
            conn = sqlite3.connect(db)
        except sqlite3.Error as e:
            raise CallError(e)

        with conn:
            cur = conn.cursor()
            cur.execute(
                f'SELECT * FROM packages WHERE origin="{pkg}" OR name="{pkg}"'
            )

            rows = cur.fetchall()

            return rows

    @private
    def start_on_boot(self):
        ioc.IOCage(rc=True).start()

    @private
    def stop_on_shutdown(self):
        ioc.IOCage(rc=True).stop()

    @private
    async def terminate(self):
        await SHUTDOWN_LOCK.acquire()


async def __event_system(middleware, event_type, args):
    """
    Method called when system is ready or shutdown, supposed to start/stop jails
    flagged that way.
    """
    # We need to call a method in Jail service to make sure it runs in the
    # process pool because of py-libzfs thread safety issue with iocage and middlewared
    if args['id'] == 'ready':
        await middleware.call('jail.start_on_boot')
    elif args['id'] == 'shutdown':
        async with SHUTDOWN_LOCK:
            await middleware.call('jail.stop_on_shutdown')


def setup(middleware):
    middleware.event_subscribe('system', __event_system)
