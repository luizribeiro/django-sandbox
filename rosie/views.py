import hashlib
import hmac
import json
from django.core.exceptions import PermissionDenied
from django.http import (
    Http404,
    HttpRequest,
    HttpResponse,
)
from django.views.decorators.csrf import csrf_exempt
from os import environ as env
from rosie.messaging import (send_message, broadcast_message)
from rosie.models import SubscribedUser
from weather import (Weather, Unit)


def _handle_received_message(
    sender_psid: str,
    text: str,
) -> None:
    if 'weather' in text.strip().lower():
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
    SubscribedUser(user_psid=sender_psid).save()
    broadcast_message("Broadcast: " + text)


@csrf_exempt
def webhook(request: HttpRequest) -> HttpResponse:
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
        _handle_received_message(
            str(message['sender']['id']),
            str(message['message']['text']),
        )

    return HttpResponse('Message Processed')

