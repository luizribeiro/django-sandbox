import hashlib
import hmac
import json
import rosie.tasks
from django.test import (
    Client,
    TestCase,
)
from os import environ as env
from django.http import HttpResponse
from rosie.models import SubscribedUser
from typing import (
    Any,
    Dict,
    List,
    NamedTuple,
)
from unittest.mock import (patch, Mock)
from util.tests import set_env


SentMessage = NamedTuple('SentMessage', [
    ('recipient_psid', str),
    ('text', str),
])


class GraphAPIMock:
    def __init__(self):
        self.requests_post_mock = patch(
            'requests.post',
            side_effect=self._mock_post,
        )
        self._messages = []

    def __enter__(self):
        self.requests_post_mock.__enter__()
        return self

    def __exit__(
        self,
        exception_type,
        exception_value,
        exception_traceback,
    ):
        self.requests_post_mock.__exit__(
            exception_type,
            exception_value,
            exception_traceback,
        )

    def _mock_post(self, uri, params={}, data={}) -> None:
        recipient = json.loads(data.get('recipient', '{}'))
        message = json.loads(data.get('message', '{}'))
        self._messages.append(SentMessage(
            recipient_psid=recipient.get('id'),
            text=message.get('text'),
        ))

    @property
    def sent_messages(self) -> List[SentMessage]:
        return self._messages

    def clear(self):
        self._messages = []


class RosieTestCase(TestCase):
    def subscribe_user(self, user_psid):
        SubscribedUser(user_psid=user_psid).save()


class RosieWebHookTests(TestCase):
    def setUp(self) -> None:
        self.client = Client()

    @set_env(ROSIE_VERIFY_TOKEN='asdfg')
    def test_failed_webhook_verification(self) -> None:
        response = self.client.get('/rosie/', {
            'hub.verify_token': 'qwerty',
            'hub.challenge': '12345',
            'hub.mode': 'subscribe',
        })
        self.assertEqual(response.status_code, 403)

    @set_env(ROSIE_VERIFY_TOKEN='asdfg')
    def test_successful_webhook_verification(self) -> None:
        response = self.client.get('/rosie/', {
            'hub.verify_token': 'asdfg',
            'hub.challenge': '12345',
            'hub.mode': 'subscribe',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'12345')

    @set_env(ROSIE_APP_SECRET='my_app_secret')
    def _call_webhook(self, content: Dict[str, Any]) -> HttpResponse:
        json_content = json.dumps(content)
        hub_signature = hmac.new(
            (env.get('ROSIE_APP_SECRET') or '').encode('utf-8'),
            json_content.encode('utf-8'),
            hashlib.sha1,
        ).hexdigest()
        return self.client.post(
            '/rosie/',
            json_content,
            content_type="application/json",
            **{'HTTP_X_HUB_SIGNATURE': 'sha1=' + hub_signature}
        )

    def test_webhook_without_signature(self) -> None:
        response = self.client.post(
            '/rosie/',
            {"object": "page"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

    def test_webhook_with_invalid_signature(self) -> None:
        response = self.client.post(
            '/rosie/',
            {"object": "page"},
            content_type="application/json",
            **{'HTTP_X_HUB_SIGNATURE': 'sha1=asdfg'}
        )
        self.assertEqual(response.status_code, 403)

    def test_webhook_called_for_another_object_type(self) -> None:
        response = self._call_webhook({"object": "something_else"})
        self.assertEqual(response.status_code, 404)

    def _send_message_to_webhook(
        self,
        sender_psid: str,
        text: str,
    ) -> HttpResponse:
        return self._call_webhook({
            'object': 'page',
            'entry': [
                {
                    'messaging': [
                        {
                            'message': {
                                'mid': 'mid.$FooBAr-',
                                'text': text,
                                'seq': 1180600,
                            },
                            'recipient': {'id': '12345'},
                            'timestamp': 1527378331528,
                            'sender': {'id': sender_psid},
                        },
                    ],
                    'id': '12345',
                    'time': 1527432965069,
                },
            ],
        })

    def test_receive_message(self) -> None:
        response = self._send_message_to_webhook('54321', 'asdfasdf')
        self.assertEqual(response.status_code, 200)

    def test_like_sticker_message(self) -> None:
        response = self._call_webhook({
            'object': 'page',
            'entry': [
                {
                    'messaging': [
                        {
                            'timestamp': 1527434293975,
                            'message': {
                                'attachments': [
                                    {
                                        'type': 'image',
                                        'payload': {
                                            'sticker_id': 369239263222822,
                                            'url': 'http://cdn.net/f.png',
                                        },
                                    },
                                ],
                                'mid': 'mid.$FooBAr-',
                                'sticker_id': 369239263222822,
                                'seq': 1180691,
                            },
                            'sender': {'id': '54321'},
                            'recipient': {'id': '12345'},
                        },
                    ],
                    'time': 1527434395008,
                    'id': '12345',
                },
            ],
        })
        self.assertEqual(response.status_code, 200)

    def test_subscribe_on_message(self) -> None:
        subscribed_users = SubscribedUser.get_all_subscribers()
        self.assertEquals(len(subscribed_users), 0)

        self._send_message_to_webhook('42', 'subscribe pls')
        subscribed_users = SubscribedUser.get_all_subscribers()
        self.assertEquals(len(subscribed_users), 1)
        self.assertEquals(subscribed_users[0].user_psid, '42')

        self._send_message_to_webhook('42', 'im already subscribed')
        subscribed_users = SubscribedUser.get_all_subscribers()
        self.assertEquals(len(subscribed_users), 1)

    def test_broadcast_on_message(self) -> None:
        with GraphAPIMock() as graph_api_mock:
            self.assertEquals(len(graph_api_mock.sent_messages), 0)

            self._send_message_to_webhook('42', 'subscribe pls')
            self.assertEquals(len(graph_api_mock.sent_messages), 1)
            self.assertEquals(graph_api_mock.sent_messages[0], SentMessage(
                recipient_psid='42',
                text='Broadcast: subscribe pls',
            ))

            graph_api_mock.clear()

            self._send_message_to_webhook('64', 'hi there')
            self.assertEquals(len(graph_api_mock.sent_messages), 2)
            self.assertIn(SentMessage(
                recipient_psid='42',
                text='Broadcast: hi there',
            ), graph_api_mock.sent_messages)
            self.assertIn(SentMessage(
                recipient_psid='64',
                text='Broadcast: hi there',
            ), graph_api_mock.sent_messages)

    def test_replies_with_weather(self) -> None:
        lookup = Mock(condition=Mock(text='Cloudy', temp='16'))
        with patch(
            'rosie.views.Weather.lookup',
            return_value=lookup,
        ), GraphAPIMock() as graph_api_mock:
            self._send_message_to_webhook('42', 'tell me the weather')
            self.assertEquals(len(graph_api_mock.sent_messages), 1)
            self.assertIn(SentMessage(
                recipient_psid='42',
                text='It is currently 16°C and Cloudy',
            ), graph_api_mock.sent_messages)


class TaskTests(RosieTestCase):
    USER_1_PSID = '1234'
    USER_2_PSID = '5678'

    def setUp(self) -> None:
        self.subscribe_user(self.USER_1_PSID)
        self.subscribe_user(self.USER_2_PSID)

    def test_broadcast_message(self) -> None:
        nest_mock = Mock(thermostats=[
            Mock(mode='off', temperature=24, target=23.5),
        ])
        weather_lookup_mock = Mock(condition=Mock(text='Sunny', temp='32'))
        with GraphAPIMock() as graph_api_mock, \
            patch('rosie.tasks.Nest', return_value=nest_mock), \
            patch('rosie.tasks.Weather.lookup', return_value=weather_lookup_mock):
            rosie.tasks.do_checks()
            self.assertEquals(len(graph_api_mock.sent_messages), 0)
            weather_lookup_mock.condition.text = 'Cloudy'
            weather_lookup_mock.condition.temp = '20'
            rosie.tasks.do_checks()
            self.assertEquals(len(graph_api_mock.sent_messages), 2)
