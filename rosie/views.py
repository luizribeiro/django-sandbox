from django.core.exceptions import PermissionDenied
from django.http import (
    HttpRequest,
    HttpResponse,
)
from os import environ as env


def receive_message(request: HttpRequest) -> HttpResponse:
    if request.method == 'GET':
        received_token = request.GET.get('hub.verify_token')
        if received_token != env.get('ROSIE_VERIFY_TOKEN'):
            raise PermissionDenied
        return HttpResponse(request.GET['hub.challenge'])
    elif request.method == 'POST':
        print(request)
        return HttpResponse('Message Processed')

