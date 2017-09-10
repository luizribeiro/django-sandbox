from backend.vacuum import (
    Vacuum,
    VacuumError,
    VacuumState,
)
from django.core.management.base import BaseCommand
from util.async import await_synchronously
import datetime
import sys
import time


def _log(s: str) -> None:
    print('[{}] {}'.format(datetime.datetime.now().isoformat(), s))
    sys.stdout.flush()


class Command(BaseCommand):
    help = 'Checks on the vacuum and restarts if necessary'

    def handle(self, *args, **options):
        while True:
            await_synchronously(self._async_check_on_vacuum())
            time.sleep(600)

    async def _async_check_on_vacuum(self) -> None:
        _log('Checking on Vacuum...')
        try:
            status = await Vacuum().async_read_status()
            state = VacuumState(status.state_code)
            error = VacuumError(status.error_code)
            _log('Status: {}, Error: {}'.format(state.name, error.name))

            if state == VacuumState.ERROR \
                    and error == VacuumError.CLEAN_MAIN_BRUSH:
                _log('Re-starting Vacuum...')
                await Vacuum().async_start()
        except Exception as e:
            _log('Failed: {}'.format(str(e)))

