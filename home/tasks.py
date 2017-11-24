import datetime
import time
import sys
from keyvaluestore.utils import get_value_or_default, set_key_value

from backend import scheduler
from home.vacuum import (
    Vacuum,
    VacuumError,
    VacuumState,
)


RESTART_TIMEOUT = [
    0,  # restart once immediately
    30 * 60,  # twice after 30 min
    24 * 60 * 60,  # then only the next day
]


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

        current_time = time.time()
        last_restart = float(get_value_or_default('last_vacuum_restart', 0))
        num_restarts = int(get_value_or_default('num_vacuum_restarts', 0))
        time_since_restart = current_time - last_restart

        if state == VacuumState.ERROR \
                and error == VacuumError.CLEAN_MAIN_BRUSH \
                and time_since_restart >= RESTART_TIMEOUT[num_restarts % 3]:
            _log('Re-starting Vacuum...')
            await Vacuum().async_start()
            set_key_value('last_vacuum_restart', current_time)
            set_key_value('num_vacuum_restarts', num_restarts + 1)
    except Exception as e:
        _log('Failed: {}'.format(str(e)))

