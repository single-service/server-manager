from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from django.conf import settings


class Command(BaseCommand):
    help = 'Init Site'


    def handle(self, *args, **options):
        Site.objects.all().update(
            domain=settings.CURRENT_HOST,
            name=settings.CURRENT_HOST,
        )
