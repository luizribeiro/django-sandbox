import home.tasks
from home.vacuum import (
    VacuumError,
    VacuumState,
)
from django.contrib.auth.models import User
from django.test import TransactionTestCase
from home.thermostat import Thermostat
from keyvaluestore.utils import get_value_or_default
import json
from os import environ as env
from rest_framework.test import APIClient
from unittest.mock import (
    patch,
    MagicMock,
)
from util.async import sync
from util.tests import captured_output


class VacuumTests(TransactionTestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username='luiz',
            email='luiz@sb.luiz.ninja',
            password='top_secret',
        )

    def test_vacuum_seq_id(self) -> None:
        current_seq_id = int(get_value_or_default('vacuum_seq', '0'))
        vacuum_mock = MagicMock(
            status=MagicMock(return_value=MagicMock(state_code=8, battery=90)),
            raw_id=93,
        )
        with patch('home.vacuum.miio.Vacuum', return_value=vacuum_mock) as vacuum:
            client = APIClient()
            client.force_authenticate(user=self.user)
            response = client.get('/graphql/', {'query': '{vacuum{state}}'})
            vacuum.assert_called_once_with(
                env.get('MIROBO_IP', '127.0.0.1'),
                env.get('MIROBO_TOKEN'),
                current_seq_id,
            )
        assert get_value_or_default('vacuum_seq', '0') == '93'
        vacuum_mock = MagicMock(
            status=MagicMock(return_value=MagicMock(state_code=8, battery=90)),
            raw_id=94,
        )
        with patch('home.vacuum.miio.Vacuum', return_value=vacuum_mock) as vacuum:
            client = APIClient()
            client.force_authenticate(user=self.user)
            response = client.get('/graphql/', {'query': '{vacuum{state}}'})
            vacuum.assert_called_once_with(
                env.get('MIROBO_IP', '127.0.0.1'),
                env.get('MIROBO_TOKEN'),
                93,
            )
        assert get_value_or_default('vacuum_seq', '0') == '94'
        assert json.loads(response.content.decode('utf-8')) == {'data': {
            'vacuum': {'state': 'CHARGING'},
        }}


class ThermostatTests(TransactionTestCase):
    @sync
    async def test_away_mode(self) -> None:
        nest_mock = MagicMock(
            thermostats=[
                MagicMock(
                    mode='off',
                    temperature=24,
                    target=23.5,
                    structure=MagicMock(away='away'),
                ),
            ],
        )
        with patch('home.thermostat.Nest', return_value=nest_mock):
            status = await Thermostat().async_read_status()
            self.assertTrue(status.is_away)
            nest_mock.thermostats[0].structure.away = 'home'
            status = await Thermostat().async_read_status()
            self.assertFalse(status.is_away)


class GraphQLQueryTests(TransactionTestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username='luiz',
            email='luiz@sb.luiz.ninja',
            password='top_secret',
        )

    def test_graphql_response(self) -> None:
        nest_mock = MagicMock(
            thermostats=[
                MagicMock(
                    mode='off',
                    temperature=24,
                    target=23.5,
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

        with patch('home.thermostat.Nest', return_value=nest_mock), \
                patch('home.vacuum.miio.Vacuum', return_value=vacuum_mock):
            client = APIClient()
            client.force_authenticate(user=self.user)
            response = client.get(
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

        with patch('home.vacuum.miio.Vacuum', return_value=vacuum_mock):
            client = APIClient(enforce_csrf_checks=True)
            client.force_authenticate(user=self.user)
            response = client.post(
                '/graphql/',
                {'query': '{vacuum{state}}'},
            )
            assert json.loads(response.content.decode('utf-8')) == {
                'data': {
                    'vacuum': {'state': 'CHARGING'},
                },
            }

    def test_unauthenticated_graphql_query(self) -> None:
        vacuum_mock = MagicMock(
            status=MagicMock(return_value=MagicMock(state_code=8, battery=90)),
            raw_id=42,
        )

        with patch('home.vacuum.miio.Vacuum', return_value=vacuum_mock):
            client = APIClient()
            response = client.get(
                '/graphql/',
                {'query': '{vacuum{state}}'},
            )
            assert json.loads(response.content.decode('utf-8')) == {
                'detail': 'Authentication credentials were not provided.',
            }


class GraphQLMutationTests(TransactionTestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username='luiz',
            email='luiz@sb.luiz.ninja',
            password='top_secret',
        )

    def test_graphql_mutation(self) -> None:
        start_mock = MagicMock()
        vacuum_mock = MagicMock(
            status=MagicMock(return_value=MagicMock(
                state_code=8,
                battery=90,
            )),
            raw_id=42,
            start=start_mock,
        )

        with patch('home.vacuum.miio.Vacuum', return_value=vacuum_mock):
            client = APIClient()
            client.force_authenticate(user=self.user)
            response = client.post(
                '/graphql/',
                {'query': 'mutation {updateVacuum(state: CLEANING) {ok}}'},
            )
            self.assertTrue(start_mock.called)
            assert json.loads(response.content.decode('utf-8')) == {
                'data': {
                    'updateVacuum': {'ok': True},
                },
            }
        assert get_value_or_default('vacuum_seq', '0') == '42'


class TaskTests(TransactionTestCase):
    @sync
    async def test_auto_restart_vacuum(self) -> None:
        vacuum_status_mock = MagicMock(
            state_code=VacuumState.CHARGING,
            error_code=VacuumError.NO_ERROR,
            battery=90,
        )
        start_mock = MagicMock()
        vacuum_mock = MagicMock(
            status=MagicMock(return_value=vacuum_status_mock),
            raw_id=42,
            start=start_mock,
        )

        with patch('home.vacuum.miio.Vacuum', return_value=vacuum_mock), \
                patch('home.tasks.time.time') as time_mock, \
                captured_output() as (stdout, stderr):
            time_mock.return_value = 1511561555.138444

            await home.tasks.check_on_vacuum()
            self.assertFalse(start_mock.called)
            self.assertTrue('Checking on Vacuum...' in stdout.getvalue())
            self.assertTrue('Re-starting Vacuum...' not in stdout.getvalue())

            # should try restarting the vacuum if stuck on carpet
            vacuum_status_mock.state_code = VacuumState.ERROR
            vacuum_status_mock.error_code = VacuumError.CLEAN_MAIN_BRUSH
            await home.tasks.check_on_vacuum()
            self.assertTrue(start_mock.called)
            self.assertTrue('Re-starting Vacuum...' in stdout.getvalue())

            # shouldn't restart sooner than 30 min
            start_mock.reset_mock()
            time_mock.return_value += 29 * 60
            await home.tasks.check_on_vacuum()
            self.assertFalse(start_mock.called)

            # after 30 min is okay
            time_mock.return_value += 1 * 60
            await home.tasks.check_on_vacuum()
            self.assertTrue(start_mock.called)

            # shouldn't start before next day
            start_mock.reset_mock()
            time_mock.return_value += 23 * 60 * 60
            await home.tasks.check_on_vacuum()
            self.assertFalse(start_mock.called)

            # next day is fine though
            time_mock.return_value += 60 * 60
            await home.tasks.check_on_vacuum()
            self.assertTrue(start_mock.called)

