from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Run automation"

    def handle(self, *args, **kwargs):
        print("Automation running...")
