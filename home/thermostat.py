from enum import Enum
from nest import Nest
from os import environ as env
from util.async import threaded_async


class ThermostatMode(Enum):
    OFF = 'off'
    ECO = 'eco'
    COOL = 'cool'
    HEAT = 'heat'
    HEAT_COOL = 'heat-cool'


class ThermostatInfo:
    def __init__(
        self,
        mode: ThermostatMode,
        current_temperature: float,
        target_temperature: float,
        is_away: bool,
    ) -> None:
        self.mode = mode
        self.current_temperature = current_temperature
        self.target_temperature = target_temperature
        self.is_away = is_away


class Thermostat:
    def __init__(self) -> None:
        self.nest = Nest(
            client_id=env.get('NEST_CLIENT_ID'),
            client_secret=env.get('NEST_CLIENT_SECRET'),
            access_token=env.get('NEST_ACCESS_TOKEN'),
        )

    @threaded_async
    def _async_read_status(self) -> ThermostatInfo:
        thermostat = self.nest.thermostats[0]
        structure = thermostat.structure
        return ThermostatInfo(
            mode=thermostat.mode,
            current_temperature=thermostat.temperature,
            target_temperature=thermostat.target,
            is_away=(structure.away == 'away'),
        )

    async def async_read_status(self) -> ThermostatInfo:
        # pyre-fixme[12] can't use @threaded_async with pyre
        return await self._async_read_status()

    @threaded_async
    def _async_set_mode(self, mode: ThermostatMode) -> None:
        thermostat = self.nest.thermostats[0]
        thermostat.mode = mode.value

    async def async_set_mode(self, mode: ThermostatMode) -> None:
        # pyre-fixme[12] can't use @threaded_async with pyre
        return await self._async_set_mode(mode)

