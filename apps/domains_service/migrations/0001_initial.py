# Generated by Django 5.1.3 on 2024-12-04 11:26

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('docker_service', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Domain',
            fields=[
                ('id', models.CharField(db_index=True, default=uuid.uuid4, editable=False, max_length=100, primary_key=True, serialize=False)),
                ('created_dt', models.DateTimeField(auto_now_add=True, verbose_name='Date of creation')),
                ('updated_dt', models.DateTimeField(auto_now=True, verbose_name='Date of update')),
                ('domain', models.URLField(verbose_name='Domain')),
                ('redirect_host', models.CharField(max_length=200, verbose_name='Redirect Host')),
                ('redirect_port', models.CharField(max_length=200, verbose_name='Redirect Port')),
                ('is_ssl', models.BooleanField(default=False, verbose_name='Is SSL')),
                ('is_prepared', models.BooleanField(default=False, verbose_name='Is prepared')),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='docker_service.service')),
            ],
            options={
                'verbose_name': 'Domain',
                'verbose_name_plural': 'Domains',
            },
        ),
        migrations.CreateModel(
            name='DomainAlias',
            fields=[
                ('id', models.CharField(db_index=True, default=uuid.uuid4, editable=False, max_length=100, primary_key=True, serialize=False)),
                ('created_dt', models.DateTimeField(auto_now_add=True, verbose_name='Date of creation')),
                ('updated_dt', models.DateTimeField(auto_now=True, verbose_name='Date of update')),
                ('alias', models.CharField(max_length=300, verbose_name='Alias')),
                ('path', models.CharField(max_length=300, verbose_name='Path')),
                ('domain', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='domains_service.domain')),
            ],
            options={
                'verbose_name': 'Domain Alias',
                'verbose_name_plural': 'Domain Aliases',
            },
        ),
    ]
