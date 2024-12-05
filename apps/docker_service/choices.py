from django.db.models import IntegerChoices, TextChoices
from django.utils.translation import gettext as _


class StackTypeChoices(IntegerChoices):
    COMPOSE = 1, 'Docker Compose'
    SWARM = 2, 'Docker Swarm'


class RestartPolicyChoices(IntegerChoices):
    ONFAILURE = 1, 'On failure'
    ALWAYS = 2, 'Always'

class ProtocolTypesChoices(TextChoices):
    HTTP = 'http', 'http'
    HTTPS = 'https', 'https'

