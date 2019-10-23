"""Rename indexes

Revision ID: ed69a9a6fab1
Revises: 74cf6ec20dcd
Create Date: 2019-10-22 17:52:07.184559+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ed69a9a6fab1'
down_revision = '74cf6ec20dcd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('account_bsdusers', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_account_bsdusers_bsdusr_group_id'), ['bsdusr_group_id'], unique=False)
        batch_op.drop_index('account_bsdusers_30f2801f')

    with op.batch_alter_table('directoryservice_activedirectory', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_directoryservice_activedirectory_ad_certificate_id'), ['ad_certificate_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_directoryservice_activedirectory_ad_kerberos_realm_id'), ['ad_kerberos_realm_id'], unique=False)
        batch_op.drop_index('directoryservice_activedirectory_a4250fac')
        batch_op.drop_index('directoryservice_activedirectory_b03e01d8')

    with op.batch_alter_table('directoryservice_idmap_ldap', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_directoryservice_idmap_ldap_idmap_ldap_certificate_id'), ['idmap_ldap_certificate_id'], unique=False)
        batch_op.drop_index('directoryservice_idmap_ldap_592ad9d0')

    with op.batch_alter_table('directoryservice_idmap_rfc2307', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_directoryservice_idmap_rfc2307_idmap_rfc2307_certificate_id'), ['idmap_rfc2307_certificate_id'], unique=False)
        batch_op.drop_index('directoryservice_idmap_rfc2307_869bf111')

    with op.batch_alter_table('directoryservice_ldap', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_directoryservice_ldap_ldap_certificate_id'), ['ldap_certificate_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_directoryservice_ldap_ldap_kerberos_realm_id'), ['ldap_kerberos_realm_id'], unique=False)
        batch_op.drop_index('directoryservice_ldap_9a19be3d')
        batch_op.drop_index('directoryservice_ldap_c6ef382f')

    with op.batch_alter_table('network_alias', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_network_alias_alias_interface_id'), ['alias_interface_id'], unique=False)
        batch_op.drop_index('network_alias_5f318ef4')

    with op.batch_alter_table('network_lagginterfacemembers', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_network_lagginterfacemembers_lagg_interfacegroup_id'), ['lagg_interfacegroup_id'], unique=False)
        batch_op.drop_index('network_lagginterfacemembers_14f52ba0')

    with op.batch_alter_table('services_ftp', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_services_ftp_ftp_ssltls_certificate_id'), ['ftp_ssltls_certificate_id'], unique=False)
        batch_op.drop_index('services_ftp_f897b229')

    with op.batch_alter_table('services_iscsitargetgroups', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_services_iscsitargetgroups_iscsi_target_id'), ['iscsi_target_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_services_iscsitargetgroups_iscsi_target_initiatorgroup_id'), ['iscsi_target_initiatorgroup_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_services_iscsitargetgroups_iscsi_target_portalgroup_id'), ['iscsi_target_portalgroup_id'], unique=False)
        batch_op.drop_index('services_iscsitargetgroups_39e2d7df')
        batch_op.drop_index('services_iscsitargetgroups_c939c4d7')
        batch_op.drop_index('services_iscsitargetgroups_dcc120ea')

    with op.batch_alter_table('services_iscsitargetportalip', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_services_iscsitargetportalip_iscsi_target_portalip_portal_id'), ['iscsi_target_portalip_portal_id'], unique=False)
        batch_op.drop_index('services_iscsitargetportalip_fe35c684')

    with op.batch_alter_table('services_iscsitargettoextent', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_services_iscsitargettoextent_iscsi_extent_id'), ['iscsi_extent_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_services_iscsitargettoextent_iscsi_target_id'), ['iscsi_target_id'], unique=False)
        batch_op.drop_index('services_iscsitargettoextent_74972900')
        batch_op.drop_index('services_iscsitargettoextent_8c3551d7')

    with op.batch_alter_table('services_openvpnclient', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_services_openvpnclient_client_certificate_id'), ['client_certificate_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_services_openvpnclient_root_ca_id'), ['root_ca_id'], unique=False)
        batch_op.drop_index('services_openvpnclient_337326e2')
        batch_op.drop_index('services_openvpnclient_86125d3c')

    with op.batch_alter_table('services_openvpnserver', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_services_openvpnserver_root_ca_id'), ['root_ca_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_services_openvpnserver_server_certificate_id'), ['server_certificate_id'], unique=False)
        batch_op.drop_index('services_openvpnserver_86125d3c')
        batch_op.drop_index('services_openvpnserver_94e62f0b')

    with op.batch_alter_table('services_s3', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_services_s3_s3_certificate_id'), ['s3_certificate_id'], unique=False)
        batch_op.drop_index('services_s3_3f8aa88e')

    with op.batch_alter_table('sharing_cifs_share', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_sharing_cifs_share_cifs_storage_task_id'), ['cifs_storage_task_id'], unique=False)
        batch_op.drop_index('sharing_cifs_share_d7a6a3ae')

    with op.batch_alter_table('storage_replication', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_storage_replication_repl_ssh_credentials_id'), ['repl_ssh_credentials_id'], unique=False)
        batch_op.drop_index('storage_replication_d46a5b35')

    with op.batch_alter_table('system_acmeregistrationbody', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_system_acmeregistrationbody_acme_id'), ['acme_id'], unique=False)
        batch_op.drop_index('system_acmeregistrationbody_1ece6752')

    with op.batch_alter_table('system_advanced', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_system_advanced_adv_syslog_tls_certificate_id'), ['adv_syslog_tls_certificate_id'], unique=False)
        batch_op.drop_index('system_advanced_64258e8d')

    with op.batch_alter_table('system_certificate', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_system_certificate_cert_acme_id'), ['cert_acme_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_system_certificate_cert_signedby_id'), ['cert_signedby_id'], unique=False)
        batch_op.drop_index('system_certificate_8dc6a655')
        batch_op.drop_index('system_certificate_c172260b')

    with op.batch_alter_table('system_certificateauthority', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_system_certificateauthority_cert_signedby_id'), ['cert_signedby_id'], unique=False)
        batch_op.drop_index('system_certificateauthority_c172260b')

    with op.batch_alter_table('system_settings', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_system_settings_stg_guicertificate_id'), ['stg_guicertificate_id'], unique=False)
        batch_op.drop_index('system_settings_cf5c60c6')

    with op.batch_alter_table('tasks_cloudsync', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_tasks_cloudsync_credential_id'), ['credential_id'], unique=False)
        batch_op.drop_index('tasks_cloudsync_3472cfe9')

    with op.batch_alter_table('vm_device', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_vm_device_vm_id'), ['vm_id'], unique=False)
        batch_op.drop_index('vm_device_0e0cecb8')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('vm_device', schema=None) as batch_op:
        batch_op.create_index('vm_device_0e0cecb8', ['vm_id'], unique=False)
        batch_op.drop_index(batch_op.f('ix_vm_device_vm_id'))

    with op.batch_alter_table('tasks_cloudsync', schema=None) as batch_op:
        batch_op.create_index('tasks_cloudsync_3472cfe9', ['credential_id'], unique=False)
        batch_op.drop_index(batch_op.f('ix_tasks_cloudsync_credential_id'))

    with op.batch_alter_table('system_settings', schema=None) as batch_op:
        batch_op.create_index('system_settings_cf5c60c6', ['stg_guicertificate_id'], unique=False)
        batch_op.drop_index(batch_op.f('ix_system_settings_stg_guicertificate_id'))

    with op.batch_alter_table('system_certificateauthority', schema=None) as batch_op:
        batch_op.create_index('system_certificateauthority_c172260b', ['cert_signedby_id'], unique=False)
        batch_op.drop_index(batch_op.f('ix_system_certificateauthority_cert_signedby_id'))

    with op.batch_alter_table('system_certificate', schema=None) as batch_op:
        batch_op.create_index('system_certificate_c172260b', ['cert_signedby_id'], unique=False)
        batch_op.create_index('system_certificate_8dc6a655', ['cert_acme_id'], unique=False)
        batch_op.drop_index(batch_op.f('ix_system_certificate_cert_signedby_id'))
        batch_op.drop_index(batch_op.f('ix_system_certificate_cert_acme_id'))

    with op.batch_alter_table('system_advanced', schema=None) as batch_op:
        batch_op.create_index('system_advanced_64258e8d', ['adv_syslog_tls_certificate_id'], unique=False)
        batch_op.drop_index(batch_op.f('ix_system_advanced_adv_syslog_tls_certificate_id'))

    with op.batch_alter_table('system_acmeregistrationbody', schema=None) as batch_op:
        batch_op.create_index('system_acmeregistrationbody_1ece6752', ['acme_id'], unique=False)
        batch_op.drop_index(batch_op.f('ix_system_acmeregistrationbody_acme_id'))

    with op.batch_alter_table('storage_replication', schema=None) as batch_op:
        batch_op.create_index('storage_replication_d46a5b35', ['repl_ssh_credentials_id'], unique=False)
        batch_op.drop_index(batch_op.f('ix_storage_replication_repl_ssh_credentials_id'))

    with op.batch_alter_table('sharing_cifs_share', schema=None) as batch_op:
        batch_op.create_index('sharing_cifs_share_d7a6a3ae', ['cifs_storage_task_id'], unique=False)
        batch_op.drop_index(batch_op.f('ix_sharing_cifs_share_cifs_storage_task_id'))

    with op.batch_alter_table('services_s3', schema=None) as batch_op:
        batch_op.create_index('services_s3_3f8aa88e', ['s3_certificate_id'], unique=False)
        batch_op.drop_index(batch_op.f('ix_services_s3_s3_certificate_id'))

    with op.batch_alter_table('services_openvpnserver', schema=None) as batch_op:
        batch_op.create_index('services_openvpnserver_94e62f0b', ['server_certificate_id'], unique=False)
        batch_op.create_index('services_openvpnserver_86125d3c', ['root_ca_id'], unique=False)
        batch_op.drop_index(batch_op.f('ix_services_openvpnserver_server_certificate_id'))
        batch_op.drop_index(batch_op.f('ix_services_openvpnserver_root_ca_id'))

    with op.batch_alter_table('services_openvpnclient', schema=None) as batch_op:
        batch_op.create_index('services_openvpnclient_86125d3c', ['root_ca_id'], unique=False)
        batch_op.create_index('services_openvpnclient_337326e2', ['client_certificate_id'], unique=False)
        batch_op.drop_index(batch_op.f('ix_services_openvpnclient_root_ca_id'))
        batch_op.drop_index(batch_op.f('ix_services_openvpnclient_client_certificate_id'))

    with op.batch_alter_table('services_iscsitargettoextent', schema=None) as batch_op:
        batch_op.create_index('services_iscsitargettoextent_8c3551d7', ['iscsi_extent_id'], unique=False)
        batch_op.create_index('services_iscsitargettoextent_74972900', ['iscsi_target_id'], unique=False)
        batch_op.drop_index(batch_op.f('ix_services_iscsitargettoextent_iscsi_target_id'))
        batch_op.drop_index(batch_op.f('ix_services_iscsitargettoextent_iscsi_extent_id'))

    with op.batch_alter_table('services_iscsitargetportalip', schema=None) as batch_op:
        batch_op.create_index('services_iscsitargetportalip_fe35c684', ['iscsi_target_portalip_portal_id'], unique=False)
        batch_op.drop_index(batch_op.f('ix_services_iscsitargetportalip_iscsi_target_portalip_portal_id'))

    with op.batch_alter_table('services_iscsitargetgroups', schema=None) as batch_op:
        batch_op.create_index('services_iscsitargetgroups_dcc120ea', ['iscsi_target_portalgroup_id'], unique=False)
        batch_op.create_index('services_iscsitargetgroups_c939c4d7', ['iscsi_target_id'], unique=False)
        batch_op.create_index('services_iscsitargetgroups_39e2d7df', ['iscsi_target_initiatorgroup_id'], unique=False)
        batch_op.drop_index(batch_op.f('ix_services_iscsitargetgroups_iscsi_target_portalgroup_id'))
        batch_op.drop_index(batch_op.f('ix_services_iscsitargetgroups_iscsi_target_initiatorgroup_id'))
        batch_op.drop_index(batch_op.f('ix_services_iscsitargetgroups_iscsi_target_id'))

    with op.batch_alter_table('services_ftp', schema=None) as batch_op:
        batch_op.create_index('services_ftp_f897b229', ['ftp_ssltls_certificate_id'], unique=False)
        batch_op.drop_index(batch_op.f('ix_services_ftp_ftp_ssltls_certificate_id'))

    with op.batch_alter_table('network_lagginterfacemembers', schema=None) as batch_op:
        batch_op.create_index('network_lagginterfacemembers_14f52ba0', ['lagg_interfacegroup_id'], unique=False)
        batch_op.drop_index(batch_op.f('ix_network_lagginterfacemembers_lagg_interfacegroup_id'))

    with op.batch_alter_table('network_alias', schema=None) as batch_op:
        batch_op.create_index('network_alias_5f318ef4', ['alias_interface_id'], unique=False)
        batch_op.drop_index(batch_op.f('ix_network_alias_alias_interface_id'))

    with op.batch_alter_table('directoryservice_ldap', schema=None) as batch_op:
        batch_op.create_index('directoryservice_ldap_c6ef382f', ['ldap_certificate_id'], unique=False)
        batch_op.create_index('directoryservice_ldap_9a19be3d', ['ldap_kerberos_realm_id'], unique=False)
        batch_op.drop_index(batch_op.f('ix_directoryservice_ldap_ldap_kerberos_realm_id'))
        batch_op.drop_index(batch_op.f('ix_directoryservice_ldap_ldap_certificate_id'))

    with op.batch_alter_table('directoryservice_idmap_rfc2307', schema=None) as batch_op:
        batch_op.create_index('directoryservice_idmap_rfc2307_869bf111', ['idmap_rfc2307_certificate_id'], unique=False)
        batch_op.drop_index(batch_op.f('ix_directoryservice_idmap_rfc2307_idmap_rfc2307_certificate_id'))

    with op.batch_alter_table('directoryservice_idmap_ldap', schema=None) as batch_op:
        batch_op.create_index('directoryservice_idmap_ldap_592ad9d0', ['idmap_ldap_certificate_id'], unique=False)
        batch_op.drop_index(batch_op.f('ix_directoryservice_idmap_ldap_idmap_ldap_certificate_id'))

    with op.batch_alter_table('directoryservice_activedirectory', schema=None) as batch_op:
        batch_op.create_index('directoryservice_activedirectory_b03e01d8', ['ad_kerberos_realm_id'], unique=False)
        batch_op.create_index('directoryservice_activedirectory_a4250fac', ['ad_certificate_id'], unique=False)
        batch_op.drop_index(batch_op.f('ix_directoryservice_activedirectory_ad_kerberos_realm_id'))
        batch_op.drop_index(batch_op.f('ix_directoryservice_activedirectory_ad_certificate_id'))

    with op.batch_alter_table('account_bsdusers', schema=None) as batch_op:
        batch_op.create_index('account_bsdusers_30f2801f', ['bsdusr_group_id'], unique=False)
        batch_op.drop_index(batch_op.f('ix_account_bsdusers_bsdusr_group_id'))
    # ### end Alembic commands ###
