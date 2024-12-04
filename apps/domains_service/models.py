from django.db import models
from django.utils.translation import gettext as _

from generic.models import AbstractBaseModel


class Domain(AbstractBaseModel):
    # Relations
    service = models.ForeignKey("docker_service.Service", on_delete=models.CASCADE)

    # Fields
    domain = models.URLField(_("Domain"), max_length=200)
    redirect_host = models.CharField(_("Redirect Host"), max_length=200)
    redirect_port = models.CharField(_("Redirect Port"), max_length=200)

    is_ssl = models.BooleanField(_("Is SSL"), default=False)
    is_prepared = models.BooleanField(_("Is prepared"), default=False)

    def __str__(self):
        return self.domain

    class Meta:
        verbose_name = _("Domain")
        verbose_name_plural = _("Domains")


class DomainAlias(AbstractBaseModel):
    # Relations
    domain = models.ForeignKey("domains_service.Domain", on_delete=models.CASCADE)

    # Fields
    alias = models.CharField(_("Alias"), max_length=300)
    path = models.CharField(_("Path"), max_length=300)

    def __str__(self):
        return self.alias

    class Meta:
        verbose_name = _("Domain Alias")
        verbose_name_plural = _("Domain Aliases")
