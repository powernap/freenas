# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-10-16 08:59
from __future__ import unicode_literals

from django.db import migrations, models
import freenasUI.freeadmin.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0030_ip_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='KeychainCredential',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('type', models.CharField(max_length=255)),
                ('attributes', freenasUI.freeadmin.models.fields.EncryptedDictField()),
            ],
            options={
                'abstract': False,
                'ordering': ['name'],
                'verbose_name': 'Keychain Credential',
                'verbose_name_plural': 'Keychain Credentials'
            },
        ),
        migrations.CreateModel(
            name='SSHCredentialsKeychainCredential',
            fields=[
            ],
            options={
                'verbose_name': 'SSH Connection',
                'verbose_name_plural': 'SSH Connections',
                'proxy': True,
            },
            bases=('system.keychaincredential',),
        ),
        migrations.CreateModel(
            name='SSHKeyPairKeychainCredential',
            fields=[
            ],
            options={
                'verbose_name': 'SSH Keypair',
                'verbose_name_plural': 'SSH Keypairs',
                'proxy': True,
            },
            bases=('system.keychaincredential',),
        ),
    ]
