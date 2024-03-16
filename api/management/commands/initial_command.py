from django.core.management.base import BaseCommand
from utils.broadcaster import Broadcaster

class Command(BaseCommand):
    help = 'Prints all book titles in the database'
    def handle(self, *args, **options):
        broadcaster = Broadcaster()
        print("追加する")
        broadcaster.add_broadcast()
        
# python manage.py migrate
# python manage.py initial_command 
# python manage.py get_tv_program_1