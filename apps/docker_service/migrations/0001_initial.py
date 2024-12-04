# Generated by Django 5.1.3 on 2024-12-04 11:05

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Container',
            fields=[
                ('id', models.CharField(db_index=True, default=uuid.uuid4, editable=False, max_length=100, primary_key=True, serialize=False)),
                ('created_dt', models.DateTimeField(auto_now_add=True, verbose_name='Date of creation')),
                ('updated_dt', models.DateTimeField(auto_now=True, verbose_name='Date of update')),
                ('name', models.CharField(max_length=200, verbose_name='Name')),
                ('image', models.CharField(max_length=300, verbose_name='Image')),
                ('healthcheck_command', models.TextField(verbose_name='Healthcheck Command')),
                ('interval', models.PositiveIntegerField(verbose_name='Healthcheck Interval')),
                ('timeout', models.PositiveIntegerField(verbose_name='Healthcheck Timeout')),
                ('retries', models.PositiveIntegerField(verbose_name='Healthcheck Retries')),
                ('start_period', models.PositiveIntegerField(verbose_name='Healthcheck Start period')),
                ('restart_policy', models.IntegerField(blank=True, choices=[(1, 'On failure'), (2, 'Always')], default=1, null=True, verbose_name='Restart Policy')),
                ('entrypoint', models.CharField(blank=True, max_length=300, null=True, verbose_name='Entrypoint')),
                ('command', models.CharField(blank=True, max_length=300, null=True, verbose_name='Command')),
            ],
            options={
                'verbose_name': 'Container',
                'verbose_name_plural': 'Containers',
            },
        ),
        migrations.CreateModel(
            name='Contour',
            fields=[
                ('id', models.CharField(db_index=True, default=uuid.uuid4, editable=False, max_length=100, primary_key=True, serialize=False)),
                ('created_dt', models.DateTimeField(auto_now_add=True, verbose_name='Date of creation')),
                ('updated_dt', models.DateTimeField(auto_now=True, verbose_name='Date of update')),
                ('name', models.CharField(max_length=200, verbose_name='Name')),
            ],
            options={
                'verbose_name': 'Contour',
                'verbose_name_plural': 'Contours',
            },
        ),
        migrations.CreateModel(
            name='DockerRegistry',
            fields=[
                ('id', models.CharField(db_index=True, default=uuid.uuid4, editable=False, max_length=100, primary_key=True, serialize=False)),
                ('created_dt', models.DateTimeField(auto_now_add=True, verbose_name='Date of creation')),
                ('updated_dt', models.DateTimeField(auto_now=True, verbose_name='Date of update')),
                ('name', models.CharField(max_length=200, verbose_name='Name')),
                ('host', models.CharField(max_length=200, verbose_name='Host')),
                ('port', models.CharField(max_length=200, verbose_name='Port')),
                ('username', models.CharField(max_length=200, verbose_name='Username')),
                ('password', models.CharField(max_length=200, verbose_name='Password')),
            ],
            options={
                'verbose_name': 'Docker Registry',
                'verbose_name_plural': 'Docker Registries',
            },
        ),
        migrations.CreateModel(
            name='Node',
            fields=[
                ('id', models.CharField(db_index=True, default=uuid.uuid4, editable=False, max_length=100, primary_key=True, serialize=False)),
                ('created_dt', models.DateTimeField(auto_now_add=True, verbose_name='Date of creation')),
                ('updated_dt', models.DateTimeField(auto_now=True, verbose_name='Date of update')),
                ('name', models.CharField(max_length=200, verbose_name='Name')),
                ('tag', models.CharField(max_length=200, verbose_name='Node Tag')),
                ('ssh_host', models.CharField(max_length=200, verbose_name='SSH Host')),
                ('ssh_username', models.CharField(max_length=200, verbose_name='SSH user')),
                ('ssh_password', models.CharField(max_length=200, verbose_name='SSH password')),
                ('current_ssh_port', models.CharField(max_length=200, verbose_name='SSH Current host')),
                ('new_ssh_port', models.CharField(max_length=200, verbose_name='SSH New host')),
                ('ssh_public_key', models.TextField(verbose_name='Your SSH Pubkey')),
                ('is_main', models.BooleanField(verbose_name='Is main')),
                ('is_prepared', models.BooleanField(default=False, verbose_name='Is prepared')),
                ('join_swarm_string', models.TextField(blank=True, null=True, verbose_name='Join String for Swarm')),
                ('contour', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='docker_service.contour')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Node',
                'verbose_name_plural': 'Nodes',
            },
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.CharField(db_index=True, default=uuid.uuid4, editable=False, max_length=100, primary_key=True, serialize=False)),
                ('created_dt', models.DateTimeField(auto_now_add=True, verbose_name='Date of creation')),
                ('updated_dt', models.DateTimeField(auto_now=True, verbose_name='Date of update')),
                ('healthcheck_command', models.TextField(verbose_name='Healthcheck Command')),
                ('interval', models.PositiveIntegerField(verbose_name='Healthcheck Interval')),
                ('timeout', models.PositiveIntegerField(verbose_name='Healthcheck Timeout')),
                ('retries', models.PositiveIntegerField(verbose_name='Healthcheck Retries')),
                ('start_period', models.PositiveIntegerField(verbose_name='Healthcheck Start period')),
                ('restart_policy', models.IntegerField(blank=True, choices=[(1, 'On failure'), (2, 'Always')], default=1, null=True, verbose_name='Restart Policy')),
                ('replicas_count', models.PositiveIntegerField(default=1, verbose_name='Replicas Count')),
                ('entrypoint', models.CharField(blank=True, max_length=300, null=True, verbose_name='Entrypoint')),
                ('command', models.CharField(blank=True, max_length=300, null=True, verbose_name='Command')),
                ('ports', models.JSONField(blank=True, help_text="e.g., [{'published': 80, 'target': 8080}]", null=True, verbose_name='Ports')),
                ('envs', models.JSONField(blank=True, help_text="e.g., {'ENV_VAR': 'value'}", null=True, verbose_name='Environment Variables')),
                ('volumes', models.JSONField(blank=True, help_text="e.g., [{'source': '/data', 'target': '/app/data'}]", null=True, verbose_name='Volumes')),
                ('update_config', models.JSONField(blank=True, help_text="e.g., {'parallelism': 2, 'delay': 5, 'failure_action': 'pause'}", null=True, verbose_name='Update Config')),
                ('rollback_config', models.JSONField(blank=True, help_text="e.g., {'parallelism': 2, 'failure_action': 'pause'}", null=True, verbose_name='Rollback Config')),
                ('container', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='docker_service.container')),
                ('stack', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='docker_service.service')),
            ],
            options={
                'verbose_name': 'Service',
                'verbose_name_plural': 'Services',
            },
        ),
        migrations.CreateModel(
            name='Stack',
            fields=[
                ('id', models.CharField(db_index=True, default=uuid.uuid4, editable=False, max_length=100, primary_key=True, serialize=False)),
                ('created_dt', models.DateTimeField(auto_now_add=True, verbose_name='Date of creation')),
                ('updated_dt', models.DateTimeField(auto_now=True, verbose_name='Date of update')),
                ('type', models.IntegerField(choices=[(1, 'Docker Compose'), (2, 'Docker Swarm')], verbose_name='Type')),
                ('name', models.CharField(max_length=200, verbose_name='Name')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('contour', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='docker_service.contour')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Stack',
                'verbose_name_plural': 'Stacks',
            },
        ),
    ]
