import json
from django.test import Client
from unittest import TestCase
from util.tests import set_env


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

    def test_webhook_called_for_another_object_type(self) -> None:
        response = self.client.post(
            '/rosie/',
            json.dumps({"object": "something_else"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)

    def test_receive_message(self) -> None:
        response = self.client.post(
            '/rosie/',
            json.dumps({
                'object': 'page',
                'entry': [
                    {
                        'messaging': [
                            {
                                'message': {
                                    'mid': 'mid.$FooBAr-',
                                    'text': 'asdfasdf',
                                    'seq': 1180600,
                                },
                                'recipient': {'id': '12345'},
                                'timestamp': 1527378331528,
                                'sender': {'id': '54321'},
                            },
                        ],
                        'id': '12345',
                        'time': 1527432965069,
                    },
                ],
            }),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

    def test_like_sticker_message(self) -> None:
        response = self.client.post(
            '/rosie/',
            json.dumps({
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
            }),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

