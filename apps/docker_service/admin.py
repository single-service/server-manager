import subprocess

from django.contrib import admin, messages
from django.utils.translation import gettext as _
from django.http import HttpRequest

import docker
import requests
from unfold.admin import ModelAdmin
from unfold.decorators import action

from .models import Contour, Container, Node, Stack, Service, DockerRegistry


@admin.register(Contour)
class ContourAdmin(ModelAdmin):
    compressed_fields = True
    warn_unsaved_form = True
    list_filter_submit = False
    list_fullwidth = False
    list_display = ["name"]

@admin.register(Node)
class NodeAdmin(ModelAdmin):
    compressed_fields = True
    warn_unsaved_form = True
    list_filter_submit = False
    list_fullwidth = False
    list_display = ["name", "is_main", "ssh_host", "tag", "is_prepared"]
    readonly_fields = ('id', 'is_prepared', 'user', 'join_swarm_string',)
    actions = ["prepare_node"]

    @action(description=_("Prepare node"))
    def prepare_node(self, request: HttpRequest, queryset):
        for node in queryset:
            subprocess.Popen(["python", "manage.py", "prepare_node", str(node.id)])
            messages.success(request, _(f"Prepare node process executed: {node.id}"))

@admin.register(DockerRegistry)
class DockerRegistryAdmin(ModelAdmin):
    compressed_fields = True
    warn_unsaved_form = True
    list_filter_submit = False
    list_fullwidth = False
    list_display = ["name"]
    actions = ["check_connection"]

    @action(description=_("Check connection"))
    def check_connection(self, request: HttpRequest, queryset):
        for registry in queryset:
            try:
                client = docker.from_env()
                client.login(username=registry.username, password=registry.password, registry=f"{registry.protocol}://{registry.host}:{registry.port}")
                # Пробуем получить список образов
                client.images.list()
                messages.success(request, f"Connection successful to {registry.name}")
            except Exception as e:
                messages.error(request, f"Connection failed to {registry.name}: {str(e)}")
        


@admin.register(Container)
class ContainerAdmin(ModelAdmin):
    compressed_fields = True
    warn_unsaved_form = True
    list_filter_submit = False
    list_fullwidth = False
    list_display = ["image"]
    actions = ["check_exist"]

    @action(description=_("Check if image exists"))
    def check_exist(self, request: HttpRequest, queryset):
        client = docker.from_env()  # Создаем клиент Docker
        for container in queryset:
            try:
                # Проверяем наличие образа в реестре
                response = requests.get(f"https://registry.hub.docker.com/v2/repositories/{container.image}/tags")
                if response.status_code == 200:
                    messages.success(request, f"Image {container.image} exists.")
                else:
                    print(response.text)
                    messages.error(request, f"Image {container.image} does not exist.")
            except Exception as e:
                messages.error(request, f"Connection failed for {container.name}: {str(e)}")


@admin.register(Stack)
class StackAdmin(ModelAdmin):
    compressed_fields = True
    warn_unsaved_form = True
    list_filter_submit = False
    list_fullwidth = False
    list_display = ["name"]


@admin.register(Service)
class ServiceAdmin(ModelAdmin):
    compressed_fields = True
    warn_unsaved_form = True
    list_filter_submit = False
    list_fullwidth = False
    list_display = ["container", "stack"]
