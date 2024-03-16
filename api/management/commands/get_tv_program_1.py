from django.core.management.base import BaseCommand
from utils.broadcaster import Broadcaster

class Command(BaseCommand):
    help = 'Prints all book titles in the database'
    def handle(self, *args, **options):
        broadcaster = Broadcaster()
        # broadcaster.get_nihonTV_program()
        # broadcaster.get_ABC_ASAHI()
        # broadcaster.get_Asahi()
        broadcaster.get_tbs()
        
