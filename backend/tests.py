from django.test import (
    Client,
    TransactionTestCase,
)
from keyvaluestore.utils import get_value_or_default
import json
from os import environ as env
from unittest.mock import (
    patch,
    MagicMock,
)


class VacuumTests(TransactionTestCase):
    def test_vacuum_seq_id(self) -> None:
        current_seq_id = int(get_value_or_default('vacuum_seq', '0'))
        vacuum_mock = MagicMock(
            status=MagicMock(return_value=MagicMock(state_code=8, battery=90)),
            raw_id=93,
        )
        with patch('home.vacuum.mirobo.Vacuum', return_value=vacuum_mock) as vacuum:
            Client().get('/graphql/', {'query': '{vacuum{state}}'})
            vacuum.assert_called_once_with(
                env.get('MIROBO_IP'),
                env.get('MIROBO_TOKEN'),
                current_seq_id,
            )
        assert get_value_or_default('vacuum_seq', '0') == '93'
        vacuum_mock = MagicMock(
            status=MagicMock(return_value=MagicMock(state_code=8, battery=90)),
            raw_id=94,
        )
        with patch('home.vacuum.mirobo.Vacuum', return_value=vacuum_mock) as vacuum:
            response = Client().get('/graphql/', {'query': '{vacuum{state}}'})
            vacuum.assert_called_once_with(
                env.get('MIROBO_IP'),
                env.get('MIROBO_TOKEN'),
                93,
            )
        assert get_value_or_default('vacuum_seq', '0') == '94'
        assert json.loads(response.content.decode('utf-8')) == {'data': {
            'vacuum': {'state': 'CHARGING'},
        }}


class GraphQLTests(TransactionTestCase):
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

        with patch('home.queries.Nest', return_value=nest_mock), \
                patch('home.vacuum.mirobo.Vacuum', return_value=vacuum_mock):
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

    def test_graphql_query_with_post_without_csrf(self) -> None:
        vacuum_mock = MagicMock(
            status=MagicMock(return_value=MagicMock(state_code=8, battery=90)),
            raw_id=42,
        )

        with patch('home.vacuum.mirobo.Vacuum', return_value=vacuum_mock):
            response = Client(enforce_csrf_checks=True).post(
                '/graphql/',
                {'query': '{vacuum{state}}'},
            )
            assert json.loads(response.content.decode('utf-8')) == {
                'data': {
                    'vacuum': {'state': 'CHARGING'},
                },
            }

