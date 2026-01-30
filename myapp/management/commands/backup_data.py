from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import transaction
from django.db.models import ForeignKey, OneToOneField
import networkx as nx

class Command(BaseCommand):
    help = 'Backup data from default database to backup database'

    def get_model_dependencies(self, models):
        """Build a dependency graph and return models in dependency order"""
        graph = nx.DiGraph()

        # Add all models to graph
        for model in models:
            graph.add_node(model)

        # Add edges for foreign key relationships
        for model in models:
            for field in model._meta.get_fields():
                if isinstance(field, (ForeignKey, OneToOneField)):
                    related_model = field.related_model
                    if related_model in models:
                        graph.add_edge(related_model, model)  # related_model must come first

        # Return models in topological order (dependencies first)
        try:
            return list(nx.topological_sort(graph))
        except nx.NetworkXError:
            # If there are cycles, just return original order
            return models

    def handle(self, *args, **options):
        # Get all models
        all_models = apps.get_models()

        # Filter out content types and other system models that might cause issues
        exclude_apps = ['contenttypes', 'sessions', 'admin']
        models_to_backup = [
            model for model in all_models
            if model._meta.app_label not in exclude_apps
        ]

        # Sort models by dependencies
        sorted_models = self.get_model_dependencies(models_to_backup)

        for model in sorted_models:
            self.stdout.write(f'Backing up {model._meta.label}...')
            try:
                with transaction.atomic(using='backup'):
                    # Get all objects from default db
                    objects = model.objects.using('default').all()
                    count = 0
                    for obj in objects:
                        # Create a copy in backup db
                        obj.pk = None  # Reset primary key to create new record
                        obj.save(using='backup')
                        count += 1
                    self.stdout.write(f'  Backed up {count} records')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  Error backing up {model._meta.label}: {e}'))
                continue

        self.stdout.write(self.style.SUCCESS('Backup completed'))