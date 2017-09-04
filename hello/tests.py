from django.test import (
    Client,
    TestCase,
)
import json
from unittest.mock import (
    patch,
    MagicMock,
)


class HelloTest(TestCase):
    def test_graphql_response(self) -> None:
        nest_mock = MagicMock(
            thermostats=[
                MagicMock(
                    mode='off',
                    current_temperature=24,
                    target_temperature=23.5,
                ),
            ],
        )
        vacuum_mock = MagicMock(
            status=MagicMock(return_value=MagicMock(
                state_code=8,
                battery=90,
            )),
            raw_id=42,
        )

        with patch('hello.schema.Nest', return_value=nest_mock), \
                patch('hello.schema.Alfred', return_value=vacuum_mock):
            response = Client().get(
                '/graphql/',
                {'query': '{thermostat{mode},vacuum{state}}'},
            )
            assert json.loads(response.content.decode('utf-8')) == {
                'data': {
                    'thermostat': {'mode': 'OFF'},
                    'vacuum': {'state': 'CHARGING'},
                },
            }

