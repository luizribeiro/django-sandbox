from graphql.execution.base import ResolveInfo
from os import environ as env
import graphene

from home.vacuum import (
    Vacuum as VacuumClient,
    VacuumState,
)
from nest import Nest
from util.async import threaded_async


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


class Vacuum(graphene.ObjectType):
    battery = graphene.Int()
    cleaned_area = graphene.Float()
    fan_speed = graphene.Int()
    state = graphene.Field(graphene.Enum.from_enum(VacuumState))


class Query(graphene.ObjectType):
    thermostat = graphene.Field(Thermostat, description='Nest Thermostat')
    vacuum = graphene.Field(Vacuum, description='Xiaomi Mi Robot Vacuum')

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

    async def resolve_vacuum(self, info: ResolveInfo) -> Vacuum:
        status = await VacuumClient().async_read_status()
        return Vacuum(
            battery=status.battery,
            cleaned_area=status.clean_area,
            fan_speed=status.fanspeed,
            state=status.state_code,
        )

