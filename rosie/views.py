import hashlib
import hmac
import json
import logging
import traceback
from django.core.exceptions import PermissionDenied
from django.http import (
    Http404,
    HttpRequest,
    HttpResponse,
)
from django.views.decorators.csrf import csrf_exempt
from home.thermostat import (
    Thermostat,
    ThermostatMode,
)
from os import environ as env
from rosie.messaging import (send_message, broadcast_message)
from rosie.models import SubscribedUser
from weather import (Weather, Unit)
from typing import Optional
from util.async import sync


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@sync
async def _handle_received_message(
    sender_psid: str,
    text: str,
    payload: Optional[str],
) -> None:
    SubscribedUser(user_psid=sender_psid).save()

    if payload == 'TURN_OFF_THERMOSTAT':
        broadcast_message("Okay! I'll go ahead and turn off the thermostat")
        await Thermostat().async_set_mode(ThermostatMode.OFF)
        return

    content = text.strip().lower()

    if 'weather' in content:
        weather = Weather(unit=Unit.CELSIUS)
        lookup = weather.lookup(12761323)
        send_message(
            sender_psid,
            'It is currently %s°C and %s' % (
                lookup.condition.temp,
                lookup.condition.text,
            ),
        )
        return

    if ('anyone' in content or 'someone' in content) and 'home' in content:
        thermostat_status = await Thermostat().async_read_status()
        send_message(
            sender_psid,
            'I don\'t think anyone is home.' if thermostat_status.is_away \
                    else 'Yup, someone is home.'
        )
        return

    send_message(sender_psid, "Sorry, I didn't understand that.")


@csrf_exempt
def webhook(request: HttpRequest) -> HttpResponse:
    logger.info(str(request.body))
    if request.method == 'GET':
        received_token = request.GET.get('hub.verify_token')
        if received_token != env.get('ROSIE_VERIFY_TOKEN'):
            raise PermissionDenied
        return HttpResponse(request.GET['hub.challenge'])

    if request.method != 'POST':
        raise Http404

    try:
        expected_signature = hmac.new(
            (env.get('ROSIE_APP_SECRET') or '').encode('utf-8'),
            request.body,
            hashlib.sha1,
        ).hexdigest()
        hub_signature = request.META['HTTP_X_HUB_SIGNATURE'].split('=')[1]
        if not hmac.compare_digest(expected_signature, hub_signature):
            raise PermissionDenied
    except BaseException:
        raise PermissionDenied

    data = json.loads(request.body.decode("utf-8"))
    if data.get('object') != 'page':
        raise Http404

    for entry in data['entry']:
        if entry.get('messaging') is None:
            continue
        message = entry['messaging'][0]
        if message.get('message') is None:
            continue
        if message['message'].get('text') is None:
            continue
        logger.info(str(message))
        sender_psid = str(message['sender']['id'])

        try:
            _handle_received_message(
                sender_psid,
                str(message['message']['text']),
                message['message'].get('quick_reply', {}).get('payload'),
            )
        except BaseException:
            error = traceback.format_exc()
            send_message(
                sender_psid,
                "Sorry. Something went wrong while handling that message. " +
                    "I hope this helps:\n\n```{}```".format(error),
            )


    return HttpResponse('Message Processed')

