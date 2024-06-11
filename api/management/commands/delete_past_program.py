from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from api.models import Program

class Command(BaseCommand):
    help = '過去の番組を削除する(前日までの番組)'

    def handle(self, *args, **options):
        print("前日までの番組データを削除します.")
        today = timezone.now() - timedelta(1)  # タイムゾーンを意識した現在時刻の取得
        end_of_yesterday = today.replace(hour=23, minute=59, second=59)  # 前日の23:59:59を設定

        programs_on_date = Program.objects.filter(
            end_time__lte=end_of_yesterday,  # 時刻を含む日時でフィルタ
        ).delete()
        print("削除完了")

        
# python3 manage.py delete_past_program