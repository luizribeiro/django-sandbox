from home.thermostat import (
    Thermostat,
    ThermostatMode,
)
from rosie.messaging import (
    broadcast_message,
    send_message,
)
from rosie.types import ReceivedMessage
from typing import (
    List,
    Optional,
)
from weather import (Weather, Unit)


def has_any_word(message: ReceivedMessage, words: List[str]) -> bool:
        return any(word in message.text for word in words)


class MessageHandler:
    def should_handle_message(self, message: ReceivedMessage) -> bool:
        raise NotImplementedError()

    async def async_handle_message(self, message: ReceivedMessage) -> None:
        pass


class PayloadMessageHandler:
    payload: Optional[str] = None

    def should_handle_message(self, message: ReceivedMessage) -> bool:
        if self.payload == None:
            raise NotImplementedError()
        return message.payload == self.payload

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
        if not has_any_word(message, ['anyone', 'someone']):
            return False

        return 'home' in message.text

    async def async_handle_message(self, message: ReceivedMessage) -> None:
        thermostat_status = await Thermostat().async_read_status()
        send_message(
            message.sender_psid,
            'I don\'t think anyone is home.' if thermostat_status.is_away \
                    else 'Yup, someone is home.'
        )


class TurnOffThermostatMessageHandler(PayloadMessageHandler):
    payload = 'TURN_OFF_THERMOSTAT'

    async def async_handle_message(self, message: ReceivedMessage) -> None:
        broadcast_message("Okay! I'll go ahead and turn off the thermostat")
        await Thermostat().async_set_mode(ThermostatMode.OFF)


class NoopMessageHandler(PayloadMessageHandler):
    payload = 'NOOP'


class YouLookNiceMessageHandler(MessageHandler):
    def should_handle_message(self, message: ReceivedMessage) -> bool:
        if not has_any_word(message, ['nice', 'beautiful', 'good', 'great']):
            return False

        return 'look' in message.text

    async def async_handle_message(self, message: ReceivedMessage) -> None:
        send_message(
            message.sender_psid,
            'Awww, you look beautiful too!',
        )

