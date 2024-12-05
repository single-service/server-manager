from django.db import models
from django.utils.translation import gettext as _

from generic.models import AbstractBaseModel
from .choices import StackTypeChoices, RestartPolicyChoices, ProtocolTypesChoices


class Contour(AbstractBaseModel):
    #Fields
    name = models.CharField(_("Name"), max_length=200)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Contour")
        verbose_name_plural = _("Contours")


class Node(AbstractBaseModel):
    # Relations
    contour = models.ForeignKey("docker_service.Contour", on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True, blank=True)

    # Fields
    name = models.CharField(_("Name"), max_length=200)
    tag = models.CharField(_("Node Tag"), max_length=200)
    ssh_host = models.CharField(_("SSH Host"), max_length=200)
    internal_ip = models.CharField(_("Internal IP"), max_length=200, null=True, default=None, blank=True)
    ssh_username = models.CharField(_("SSH user"), max_length=200)
    ssh_password = models.CharField(_("SSH password"), max_length=200)
    current_ssh_port = models.CharField(_("SSH Current host"), max_length=200)
    new_ssh_port = models.CharField(_("SSH New host"), max_length=200)
    ssh_public_key = models.TextField(_("Your SSH Pubkey"))
    is_main = models.BooleanField(_("Is main"))
    is_prepared = models.BooleanField(_("Is prepared"), default=False)
    join_swarm_string = models.TextField(_("Join String for Swarm"), null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Node")
        verbose_name_plural = _("Nodes")


class Stack(AbstractBaseModel):
    # Relations
    contour = models.ForeignKey("docker_service.Contour", on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True, blank=True)
    type = models.IntegerField(_("Type"), choices=StackTypeChoices.choices)

    # Fields
    name = models.CharField(_("Name"), max_length=200)
    description = models.TextField(_("Description"), blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Stack")
        verbose_name_plural = _("Stacks")


class Container(AbstractBaseModel):
    # Fields
    name = models.CharField(_("Name"), max_length=200)
    image = models.CharField(_("Image"), max_length=300)

    healthcheck_command = models.TextField(_("Healthcheck Command"), null=True, blank=True)
    interval = models.PositiveIntegerField(_("Healthcheck Interval"), null=True, blank=True)
    timeout = models.PositiveIntegerField(_("Healthcheck Timeout"), null=True, blank=True)
    retries = models.PositiveIntegerField(_("Healthcheck Retries"), null=True, blank=True)
    start_period = models.PositiveIntegerField(_("Healthcheck Start period"), null=True, blank=True)

    restart_policy = models.IntegerField(
        _("Restart Policy"),
        choices=RestartPolicyChoices.choices,
        null=True,
        blank=True,
        default=RestartPolicyChoices.ONFAILURE
    )

    entrypoint = models.CharField(_("Entrypoint"), max_length=300, null=True, blank=True)
    command = models.CharField(_("Command"), max_length=300, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Container")
        verbose_name_plural = _("Containers")


class Service(AbstractBaseModel):
    # Relations
    stack = models.ForeignKey("docker_service.Service", on_delete=models.CASCADE)
    container = models.ForeignKey("docker_service.Container", on_delete=models.CASCADE)

    healthcheck_command = models.TextField(_("Healthcheck Command"), null=True, blank=True)
    interval = models.PositiveIntegerField(_("Healthcheck Interval"), null=True, blank=True)
    timeout = models.PositiveIntegerField(_("Healthcheck Timeout"), null=True, blank=True)
    retries = models.PositiveIntegerField(_("Healthcheck Retries"), null=True, blank=True)
    start_period = models.PositiveIntegerField(_("Healthcheck Start period"), null=True, blank=True)

    restart_policy = models.IntegerField(
        _("Restart Policy"),
        choices=RestartPolicyChoices.choices,
        null=True,
        blank=True,
        default=RestartPolicyChoices.ONFAILURE
    )
    replicas_count = models.PositiveIntegerField(_("Replicas Count"), default=1)

    entrypoint = models.CharField(_("Entrypoint"), max_length=300, null=True, blank=True)
    command = models.CharField(_("Command"), max_length=300, null=True, blank=True)

    # Additional configurations
    ports = models.JSONField(_("Ports"), null=True, blank=True, help_text=_("e.g., [{'published': 80, 'target': 8080}]"))
    envs = models.JSONField(_("Environment Variables"), null=True, blank=True, help_text=_("e.g., {'ENV_VAR': 'value'}"))
    volumes = models.JSONField(_("Volumes"), null=True, blank=True, help_text=_("e.g., [{'source': '/data', 'target': '/app/data'}]"))

    # Update config
    update_config = models.JSONField(
        _("Update Config"),
        null=True,
        blank=True,
        help_text=_("e.g., {'parallelism': 2, 'delay': 5, 'failure_action': 'pause'}")
    )

    # Rollback config
    rollback_config = models.JSONField(
        _("Rollback Config"),
        null=True,
        blank=True,
        help_text=_("e.g., {'parallelism': 2, 'failure_action': 'pause'}")
    )

    def __str__(self):
        return f"{self.stack.name} {self.container.name}"

    class Meta:
        verbose_name = _("Service")
        verbose_name_plural = _("Services")


class DockerRegistry(AbstractBaseModel):
    # Fields
    name = models.CharField(_("Name"), max_length=200)
    host = models.CharField(_("Host"), max_length=200)
    port = models.CharField(_("Port"), max_length=200)
    username = models.CharField(_("Username"), max_length=200)
    password = models.CharField(_("Password"), max_length=200)
    protocol = models.CharField(_("Protocol type"), max_length=20, choices=ProtocolTypesChoices.choices, default=ProtocolTypesChoices.HTTP)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Docker Registry")
        verbose_name_plural = _("Docker Registries")
