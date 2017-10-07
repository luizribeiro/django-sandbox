from enum import Enum
from keyvaluestore.utils import get_value_or_default, set_key_value
from os import environ
from util.async import threaded_async
import miio


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


class Vacuum:
    def __init__(self) -> None:
        self._vacuum = miio.Vacuum(
            environ.get('MIROBO_IP'),
            environ.get('MIROBO_TOKEN'),
            int(get_value_or_default('vacuum_seq', '0')),
        )

    @threaded_async
    def async_read_status(self) -> miio.VacuumStatus:
        status = self._vacuum.status()
        set_key_value('vacuum_seq', str(self._vacuum.raw_id))
        return status

    @threaded_async
    def async_start(self) -> None:
        self._vacuum.start()
        set_key_value('vacuum_seq', str(self._vacuum.raw_id))

    def set_state(self, state: VacuumState) -> None:
        if state == VacuumState.CLEANING.value:
            self._vacuum.start()
        elif state == VacuumState.PAUSED.value:
            self._vacuum.pause()
        elif state == VacuumState.CHARGING.value:
            self._vacuum.home()
        set_key_value('vacuum_seq', str(self._vacuum.raw_id))

