from graphql.execution.base import ResolveInfo
from keyvaluestore.utils import get_value_or_default, set_key_value
from mirobo import Vacuum as Alfred
from nest import Nest
from os import environ as env
from util.async import threaded_async
import graphene


class ThermostatMode(graphene.Enum):
    OFF = 'off'
    ECO = 'eco'
    COOL = 'cool'
    HEAT = 'heat'
    HEAT_COOL = 'heat-cool'


class Thermostat(graphene.ObjectType):
    mode = graphene.Field(ThermostatMode)
    current_temperature = graphene.Float()
    target_temperature = graphene.Float()


class VacuumState(graphene.Enum):
    CHARGER_DISCONNECTED = 2
    IDLE = 3
    CLEANING = 5
    RETURNING_HOME = 6
    MANUAL_MODE = 7
    CHARGING = 8
    PAUSED = 10
    SPOT_CLEANING = 11
    ERROR = 12
    UPDATING = 14


class Vacuum(graphene.ObjectType):
    battery = graphene.Int()
    cleaned_area = graphene.Float()
    fan_speed = graphene.Int()
    state = graphene.Field(VacuumState)


class Query(graphene.ObjectType):
    thermostat = graphene.Field(Thermostat, description='Nest Thermostat')
    vacuum = graphene.Field(Vacuum, description='Nest Thermostat')

    @threaded_async
    def resolve_thermostat(self, info: ResolveInfo) -> Thermostat:
        nest = Nest(
            client_id=env.get('NEST_CLIENT_ID'),
            client_secret=env.get('NEST_CLIENT_SECRET'),
            access_token=env.get('NEST_ACCESS_TOKEN'),
        )
        thermostat = nest.thermostats[0]
        return Thermostat(
            mode=thermostat.mode,
            current_temperature=thermostat.temperature,
            target_temperature=thermostat.target,
        )

    @threaded_async
    def resolve_vacuum(self, info: ResolveInfo) -> Vacuum:
        seq_id = int(get_value_or_default('vacuum_seq', '0'))
        alfred = Alfred(env.get('MIROBO_IP'), env.get('MIROBO_TOKEN'), seq_id)
        status = alfred.status()
        set_key_value('vacuum_seq', str(alfred.raw_id))
        return Vacuum(
            battery=status.battery,
            cleaned_area=status.clean_area,
            fan_speed=status.fanspeed,
            state=status.state_code,
        )


schema = graphene.Schema(query=Query)

