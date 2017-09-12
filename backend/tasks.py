import datetime
import sys

from backend import scheduler
from backend.vacuum import (
    Vacuum,
    VacuumError,
    VacuumState,
)


def _log(s: str) -> None:
    print('[{}] {}'.format(datetime.datetime.now().isoformat(), s))
    sys.stdout.flush()


@scheduler.scheduled_job('interval', minutes=10)
async def check_on_vacuum() -> None:
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

