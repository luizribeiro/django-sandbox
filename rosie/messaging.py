import json
import requests
from os import environ as env
from rosie.models import SubscribedUser


def send_message(
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


def broadcast_message(text: str) -> None:
    for subscriber in SubscribedUser.get_all_subscribers():
        send_message(subscriber.user_psid, text)

