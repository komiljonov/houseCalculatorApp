from typing import Any
from os import getenv
from django.core.management import BaseCommand
from tg_bot import Bot















class Command(BaseCommand):



    def handle(self, *args: Any, **options: Any) -> str | None:
        TOKEN = getenv("TOKEN")

        Bot(TOKEN)



