from django.core.management.base import BaseCommand
from myapp.models import ServiceCode

class Command(BaseCommand):
    help = 'Refresh the service code validation cache'

    def handle(self, *args, **options):
        ServiceCode.refresh_cache()
        self.stdout.write(
            self.style.SUCCESS('Successfully refreshed service code cache')
        )