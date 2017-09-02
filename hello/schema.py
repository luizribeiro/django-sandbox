from mirobo import Vacuum as Alfred
from nest import Nest
from os import environ as env
import graphene


vacuum_id = 0


class Thermostat(graphene.ObjectType):
    mode = graphene.String()
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
    state = graphene.Field(VacuumState)


class Query(graphene.ObjectType):
    thermostat = graphene.Field(Thermostat, description='Nest Thermostat')
    vacuum = graphene.Field(Vacuum, description='Nest Thermostat')

    def resolve_thermostat(self, info):
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

    def resolve_vacuum(self, info):
        global vacuum_id
        alfred = Alfred(env.get('MIROBO_IP'), env.get('MIROBO_TOKEN'), vacuum_id)
        status = alfred.status()
        vacuum_id = alfred.raw_id
        return Vacuum(
            battery=status.battery,
            state=status.state_code,
        )


schema = graphene.Schema(query=Query)

