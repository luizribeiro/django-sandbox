from backend import scheduler
from home.thermostat import Thermostat
from os import environ as env
from rosie.messaging import (
    QuickReply,
    broadcast_message,
)
from util.rate_limit import should_rate_limit
from weather import (Weather, Unit)


async def _async_check_if_should_open_windows() -> None:
    weather = Weather(unit=Unit.CELSIUS)
    lookup = weather.lookup(12761323)

    thermostat = await Thermostat().async_read_status()

    if float(lookup.condition.temp) >= float(thermostat.target_temperature):
        # it is hot outside
        return

    if should_rate_limit('_check_if_should_open_windows', once_every=3600*12):
        # we've sent this message recently
        return

    broadcast_message(
        ('Can you open the windows, please? It is currently %s°C and %s' +
            ' outside. The target temperature for the thermostat is' +
            ' %.1f°C.') % (
                lookup.condition.temp,
                lookup.condition.text,
                float(thermostat.target_temperature),
            ),
        [
            QuickReply('text', 'Sure!', 'TURN_OFF_THERMOSTAT'),
            QuickReply('text', 'Not today', 'NOOP'),
        ],
    )



@scheduler.scheduled_job('interval', minutes=5)
async def async_do_checks() -> None:
    await _async_check_if_should_open_windows()

