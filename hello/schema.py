from mirobo import Vacuum as Alfred
from nest import Nest
from os import environ as env
import graphene


class Thermostat(graphene.ObjectType):
    mode = graphene.String()
    current_temperature = graphene.Float()
    target_temperature = graphene.Float()


class Vacuum(graphene.ObjectType):
    battery = graphene.String()
    state = graphene.String()


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
        alfred = Alfred(env.get('MIROBO_IP'), env.get('MIROBO_TOKEN'))
        status = alfred.status()
        return Vacuum(
            battery=status.battery,
            state=status.state,
        )


schema = graphene.Schema(query=Query)

