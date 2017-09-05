from django.core.management.base import BaseCommand
from enum import Enum
from keyvaluestore.utils import get_value_or_default, set_key_value
from mirobo import Vacuum
from os import environ as env
import datetime
import sys
import time


def _log(s: str) -> None:
    print('[{}] {}'.format(datetime.datetime.now().isoformat(), s))
    sys.stdout.flush()


class VacuumState(Enum):
    CHARGER_DISCONNECTED = 2
    IDLE = 3
    CLEANING = 5
    RETURNING_HOME = 6
    MANUAL_MODE = 7
    CHARGING = 8
    PAUSED = 10
    SPOT_CLEANING = 11
    ERROR = 12
    UPDATING = 14


class VacuumError(Enum):
    NO_ERROR = 0
    LASER_DISTANCE_SENSOR_ERROR = 1
    COLLISION_SENSOR_ERROR = 2
    WHEELS_ON_TOP_OF_VOID = 3
    CLEAN_HOVERING_SENSORS = 4
    CLEAN_MAIN_BRUSH = 5
    CLEAN_SIDE_BRUSH = 6
    MAIN_WHEEL_STUCK = 7
    DEVICE_STUCK = 8
    DUST_COLLECTOR_MISSING = 9
    CLEAN_FILTER = 10
    STUCK_IN_MAGNETIC_BARRIER = 11
    LOW_BATTERY = 12
    CHARGING_FAULT = 13
    BATTERY_FAULT = 14
    WALL_SENSORS_DIRTY = 15
    PLACE_ME_ON_FLAT_SURFACE = 16
    SIDE_BRUSHES_PROBLEM = 17
    SUCTION_FAN_PROBLEM = 18
    UNPOWERED_CHARGING_STATION = 19


class Command(BaseCommand):
    help = 'Checks on the vacuum and restarts if necessary'

    def handle(self, *args, **options):
        while True:
            self._check_on_vacuum()

    def _check_on_vacuum(self) -> None:
        _log('Checking on Vacuum...')
        try:
            seq_id = int(get_value_or_default('vacuum_seq', '0'))
            vacuum = Vacuum(
                env.get('MIROBO_IP'),
                env.get('MIROBO_TOKEN'),
                seq_id,
            )
            status = vacuum.status()

            set_key_value('vacuum_seq', str(vacuum.raw_id))
            state = VacuumState(status.state_code)
            error = VacuumError(status.error_code)
            _log('Status: {}, Error: {}'.format(state.name, error.name))

            if state == VacuumState.ERROR \
                    and error == VacuumError.CLEAN_MAIN_BRUSH:
                _log('Re-starting Vacuum...')
                vacuum.start()
        except Exception as e:
            _log('Failed: {}'.format(str(e)))
        time.sleep(600)

