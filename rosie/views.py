import json
import logging
import requests
from django.core.exceptions import PermissionDenied
from django.http import (
    Http404,
    HttpRequest,
    HttpResponse,
)
from django.views.decorators.csrf import csrf_exempt
from os import environ as env


logger = logging.getLogger(__name__)


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
            "message": json.dumps({
                "text": "Received: " + text,
            })
        },
    )


@csrf_exempt
def webhook(request: HttpRequest) -> HttpResponse:
    if request.method == 'GET':
        received_token = request.GET.get('hub.verify_token')
        logger.info('token verification')
        if received_token != env.get('ROSIE_VERIFY_TOKEN'):
            logger.info('denied')
            raise PermissionDenied
        logger.info('all good!')
        return HttpResponse(request.GET['hub.challenge'])

    if request.method != 'POST':
        logger.info('got ' + request.method)
        raise Http404

    logger.info(request.body)
    data = json.loads(request.body.decode("utf-8"))
    logger.info(data)
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
            int(message['sender']['id']),
            str(message['message']['text']),
        )

    return HttpResponse('Message Processed')

