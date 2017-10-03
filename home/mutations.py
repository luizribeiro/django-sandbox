from graphql.execution.base import ResolveInfo
import graphene

from home.graphql_common import VacuumState
from home.vacuum import Vacuum


class UpdateVacuum(graphene.Mutation):
    class Arguments:
        state = graphene.Argument(VacuumState)

    ok = graphene.Boolean()

    def mutate(self, info: ResolveInfo, state: VacuumState) -> 'UpdateVacuum':
        Vacuum().set_state(state)
        return UpdateVacuum(ok=True)


class Mutation(graphene.ObjectType):
    update_vacuum = UpdateVacuum.Field()

