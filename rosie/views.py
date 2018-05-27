import json
import requests
from django.core.exceptions import PermissionDenied
from django.http import (
    Http404,
    HttpRequest,
    HttpResponse,
)
from os import environ as env


def _handle_received_message(
    sender_psid: int,
    text: str,
) -> None:
    requests.post(
        "https://graph.facebook.com/v2.6/me/messages",
        params={
            "access_token": env.get('ROSIE_PAGE_ACCESS_TOKEN'),
        },
        data={
            "recipient": json.dumps({
                "id": str(sender_psid),
            }),
            "message": "Received: " + text,
        },
    )


def webhook(request: HttpRequest) -> HttpResponse:
    if request.method == 'GET':
        received_token = request.GET.get('hub.verify_token')
        if received_token != env.get('ROSIE_VERIFY_TOKEN'):
            raise PermissionDenied
        return HttpResponse(request.GET['hub.challenge'])

    if request.method != 'POST':
        raise Http404

    data = json.loads(request.body.decode("utf-8"))
    if data.get('object') != 'page':
        raise Http404

    for entry in data['entry']:
        if entry.get('messaging') is None:
            continue
        message = entry['messaging'][0]
        _handle_received_message(
            int(message['sender']['id']),
            str(message['text']),
        )

    return HttpResponse('Message Processed')

