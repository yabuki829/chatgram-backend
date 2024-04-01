from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings

from django.contrib.auth import get_user_model

class Command(BaseCommand):
    def handle(self, *args, **options):
        print("--------------------------------------------------------------------------")
        print("1. スーパーユーザを作成するコマンドです")
        print("--------------------------------------------------------------------------")
        User = get_user_model()
        if not User.objects.filter(email=settings.SUPERUSER_EMAIL).exists():
            print("--------------------------------------------------------------------------")
            print("2. スーパーユーザーを作成します。")
            print("--------------------------------------------------------------------------")
            user = User.objects.create_superuser(
                email=settings.SUPERUSER_EMAIL,
                username=settings.SUPER_USERNANE,
                password=settings.SUPERUSER_PASSWORD
            )
            print("--------------------------------------------------------------------------")
            print("3. スーパーユーザー作成が完了しました。")
            print("--------------------------------------------------------------------------")
            
           
        
        else:
            print("--------------------------------------------------------------------------")
            print("2.作成済みです")
            print("--------------------------------------------------------------------------")