from django.core.management.base import BaseCommand, CommandError
from item.models import Item
import pghistory

class Command(BaseCommand):

    def handle(self, *args, **options):
        test = pghistory.get_event_model(Item, 'item.snapshot')