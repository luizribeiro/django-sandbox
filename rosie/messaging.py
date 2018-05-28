import json
import requests
from os import environ as env
from rosie.models import SubscribedUser
from typing import (
    Any,
    Dict,
    List,
    NamedTuple,
    Optional,
)


QuickReply = NamedTuple('QuickReply', [
    ('content_type', str),
    ('title', str),
    ('payload', Optional[str]),
])

def quick_reply_to_dict(quick_reply: QuickReply) -> Dict[str, Any]:
    ret = {
        'content_type': quick_reply.content_type,
        'title': quick_reply.title,
    }
    if quick_reply.payload:
        ret['payload'] = quick_reply.payload
    return ret


def send_message(
    receiver_psid: str,
    text: str,
    quick_replies: Optional[List[QuickReply]] = None,
) -> None:
    message = {"text": text}  #type: Dict[str, Any]
    if quick_replies:
        message['quick_replies'] = [
            quick_reply_to_dict(quick_reply)
            for quick_reply in quick_replies
        ]
    requests.post(
        "https://graph.facebook.com/v2.6/me/messages",
        params={
            "access_token": env.get('ROSIE_PAGE_ACCESS_TOKEN'),
        },
        data={
            "recipient": json.dumps({"id": receiver_psid}),
            "message": json.dumps(message),
        },
    )


def broadcast_message(
    text: str,
    quick_replies: Optional[List[QuickReply]] = None,
) -> None:
    for subscriber in SubscribedUser.get_all_subscribers():
        send_message(subscriber.user_psid, text, quick_replies)

