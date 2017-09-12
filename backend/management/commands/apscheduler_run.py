from django.conf import settings
from django.core.management.base import BaseCommand
from importlib import import_module
import asyncio

from backend import scheduler


class Command(BaseCommand):
    help = 'Runs apscheduler tasks'

    def handle(self, *args, **options):
        scheduler.start()

        for app in settings.INSTALLED_APPS:
            try:
                import_module('.tasks', app)
                print('Loaded tasks from {}.tasks'.format(app))
            except ImportError as ex:
                pass

        try:
            asyncio.get_event_loop().run_forever()
        except (KeyboardInterrupt, SystemExit):
            pass

