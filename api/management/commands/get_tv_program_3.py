from django.core.management.base import BaseCommand
from utils.broadcaster import Broadcaster

class Command(BaseCommand):
    help = 'Prints all book titles in the database'
    def handle(self, *args, **options):
        broadcaster = Broadcaster()
        broadcaster.get_nhk_etv()
        broadcaster.get_nhk_sougou()
        broadcaster.get_tv_tokyo()
        
