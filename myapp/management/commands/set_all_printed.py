from django.core.management.base import BaseCommand
from myapp.models import Package

class Command(BaseCommand):
    help = 'Set all packages to printed=True'

    def handle(self, *args, **options):
        packages = Package.objects.all()
        count = packages.update(printed=True)
        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated {count} packages to printed=True')
        )