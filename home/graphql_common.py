import graphene

from home.vacuum import VacuumState as VacuumStateEnum


VacuumState = graphene.Enum.from_enum(VacuumStateEnum)

