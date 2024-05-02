from django.core.management.base import BaseCommand
from utils.broadcaster import Broadcaster
from datetime import time,datetime,timedelta
from api.models import Program

class Command(BaseCommand):
    help = '過去の番組を削除する(前日までの番組)'
    def handle(self, *args, **options):
        print("前日までの番組データを削除します.")
        today = datetime.now() - timedelta(1)
        formatted_date = today.strftime('%Y-%m-%d')

        programs_on_date = Program.objects.filter(
            end_time__lte=formatted_date,
        ).delete()
        print("削除完了")
        
# python3 delete_past_program