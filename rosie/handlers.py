from home.thermostat import (
    Thermostat,
    ThermostatMode,
)
from rosie.messaging import (
    broadcast_message,
    send_message,
)
from rosie.types import ReceivedMessage
from weather import (Weather, Unit)


class MessageHandler:
    def should_handle_message(self, message: ReceivedMessage) -> bool:
        raise NotImplementedError()

    async def async_handle_message(self, message: ReceivedMessage) -> None:
        pass


class WeatherMessageHandler(MessageHandler):
    def should_handle_message(self, message: ReceivedMessage) -> bool:
        return 'weather' in message.text

    async def async_handle_message(self, message: ReceivedMessage) -> None:
        weather = Weather(unit=Unit.CELSIUS)
        lookup = weather.lookup(12761323)
        send_message(
            message.sender_psid,
            'It is currently %s°C and %s' % (
                lookup.condition.temp,
                lookup.condition.text,
            ),
        )


class IsAnyoneHomeMessageHandler(MessageHandler):
    def should_handle_message(self, message: ReceivedMessage) -> bool:
        if 'anyone' not in message.text and 'someone' not in message.text:
            return False

        return 'home' in message.text

    async def async_handle_message(self, message: ReceivedMessage) -> None:
        thermostat_status = await Thermostat().async_read_status()
        send_message(
            message.sender_psid,
            'I don\'t think anyone is home.' if thermostat_status.is_away \
                    else 'Yup, someone is home.'
        )


class TurnOffThermostatMessageHandler(MessageHandler):
    def should_handle_message(self, message: ReceivedMessage) -> bool:
        return message.payload == 'TURN_OFF_THERMOSTAT'

    async def async_handle_message(self, message: ReceivedMessage) -> None:
        broadcast_message("Okay! I'll go ahead and turn off the thermostat")
        await Thermostat().async_set_mode(ThermostatMode.OFF)


class YouLookNiceMessageHandler(MessageHandler):
    def should_handle_message(self, message: ReceivedMessage) -> bool:
        if not any(word in message.text for word in ['nice', 'beautiful', 'good', 'great']):
            return False

        return 'look' in message.text

    async def async_handle_message(self, message: ReceivedMessage) -> None:
        send_message(
            message.sender_psid,
            'Awww, you look beautiful too!',
        )

