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

