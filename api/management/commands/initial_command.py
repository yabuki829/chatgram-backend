from django.core.management.base import BaseCommand
from utils.broadcaster import Broadcaster

class Command(BaseCommand):
    help = 'Prints all book titles in the database'
    def handle(self, *args, **options):
        broadcaster = Broadcaster()
        broadcaster.add_broadcast()
        
# python manage.py migrate
# python manage.py initial_command 
# python manage.py get_tv_program_1
#   python manage.py get_asahi
# python manage.py get_tvosaka
        
# eroku logs --tail --app chatgram