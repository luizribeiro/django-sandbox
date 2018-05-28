from graphql.execution.base import ResolveInfo
from os import environ as env
import graphene

from home.graphql_common import VacuumState
from home.thermostat import (
    Thermostat as ThermostatClient,
    ThermostatMode,
)
from home.vacuum import Vacuum as VacuumClient


class Thermostat(graphene.ObjectType):
    mode = graphene.Field(graphene.Enum.from_enum(ThermostatMode))
    current_temperature = graphene.Float()
    target_temperature = graphene.Float()


class Vacuum(graphene.ObjectType):
    battery = graphene.Int()
    cleaned_area = graphene.Float()
    fan_speed = graphene.Int()
    state = graphene.Field(VacuumState)


class Query(graphene.ObjectType):
    thermostat = graphene.Field(Thermostat, description='Nest Thermostat')
    vacuum = graphene.Field(Vacuum, description='Xiaomi Mi Robot Vacuum')

    async def resolve_thermostat(self, info: ResolveInfo) -> Thermostat:
        status = await ThermostatClient().async_read_status()
        return Thermostat(
            mode=status.mode,
            current_temperature=status.current_temperature,
            target_temperature=status.target_temperature,
        )

    async def resolve_vacuum(self, info: ResolveInfo) -> Vacuum:
        status = await VacuumClient().async_read_status()
        return Vacuum(
            battery=status.battery,
            cleaned_area=status.clean_area,
            fan_speed=status.fanspeed,
            state=status.state_code,
        )

