from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "テストコマンド"

    def handle(self, *args, **options):
        print('Hello World!')