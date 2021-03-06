from apscheduler.jobstores.memory import MemoryJobStore
from django.conf import settings
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from importlib import import_module
import asyncio

from backend import scheduler


class Command(BaseCommand):
    help = 'Runs apscheduler tasks'

    def handle(self, *args, **options):
        for app in settings.INSTALLED_APPS:
            try:
                import_module('.tasks', app)
                print('Loaded tasks from {}.tasks'.format(app))
            except ImportError as ex:
                pass

        scheduler.add_jobstore(MemoryJobStore(), 'default')
        scheduler.add_jobstore(DjangoJobStore(), 'django')
        scheduler.start()

        try:
            asyncio.get_event_loop().run_forever()
        except (KeyboardInterrupt, SystemExit):
            pass

