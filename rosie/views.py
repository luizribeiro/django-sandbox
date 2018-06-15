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
from os import environ as env
from rosie.handlers import MessageHandler
from rosie.messaging import (send_message, broadcast_message)
from rosie.models import SubscribedUser
from rosie.types import ReceivedMessage
from typing import (
    Any,
    Dict,
)
from util.async import sync


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@sync
async def _handle_received_message(message: ReceivedMessage) -> None:
    SubscribedUser(user_psid=message.sender_psid).save()

    for message_handler_class in MessageHandler.__subclasses__():
        message_handler = message_handler_class()
        if not message_handler.should_handle_message(message):
            continue
        await message_handler.async_handle_message(message)
        return

    send_message(message.sender_psid, "Sorry, I didn't understand that.")


def _parse_message(message: Dict[str, Any]) -> ReceivedMessage:
    return ReceivedMessage(
        sender_psid=str(message['sender']['id']),
        text=str(message['message']['text']).strip().lower(),
        payload=message['message'].get('quick_reply', {}).get('payload'),
    )


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

        parsed_message = _parse_message(message)

        try:
            _handle_received_message(parsed_message)
        except BaseException:
            error = traceback.format_exc()
            send_message(
                parsed_message.sender_psid,
                "Sorry. Something went wrong while handling that message. " +
                    "I hope this helps:\n\n```{}```".format(error),
            )


    return HttpResponse('Message Processed')

