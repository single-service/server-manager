import uuid

from django.db import models
from django.utils.translation import gettext as _


class AbstractBaseModel(models.Model):
    # Fields
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length=100, db_index=True)
    created_dt = models.DateTimeField(_('Date of creation'), auto_now_add=True, editable=False)
    updated_dt = models.DateTimeField(_('Date of update'), auto_now=True, editable=True)

    class Meta:
        abstract = True
