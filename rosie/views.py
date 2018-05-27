import hashlib
import hmac
import json
import requests
from django.core.exceptions import PermissionDenied
from django.http import (
    Http404,
    HttpRequest,
    HttpResponse,
)
from django.views.decorators.csrf import csrf_exempt
from os import environ as env
from rosie.models import SubscribedUser


def _send_message(
    receiver_psid: str,
    text: str,
) -> None:
    requests.post(
        "https://graph.facebook.com/v2.6/me/messages",
        params={
            "access_token": env.get('ROSIE_PAGE_ACCESS_TOKEN'),
        },
        data={
            "recipient": json.dumps({"id": receiver_psid}),
            "message": json.dumps({"text": text})
        },
    )


def _broadcast_to_all_subscribers(text: str) -> None:
    for subscriber in SubscribedUser.objects.all():
        _send_message(subscriber.user_psid, text)


def _handle_received_message(
    sender_psid: str,
    text: str,
) -> None:
    SubscribedUser(user_psid=sender_psid).save()
    _broadcast_to_all_subscribers("Broadcast: " + text)


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

