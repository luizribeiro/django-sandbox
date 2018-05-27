from django.conf import settings
from importlib import import_module
import graphene
from typing import cast


def _build_query() -> graphene.ObjectType:
    bases = []
    for app in settings.INSTALLED_APPS:
        try:
            queries = import_module('.queries', app)
            bases.append(queries.Query)  # type: ignore
        except ImportError:
            pass
    bases.append(graphene.ObjectType)
    return cast(
        graphene.ObjectType,
        type('Query', tuple(bases), {}),
    )


def _build_mutation() -> graphene.ObjectType:
    bases = []
    for app in settings.INSTALLED_APPS:
        try:
            mutations = import_module('.mutations', app)
            bases.append(mutations.Mutation)  # type: ignore
        except ImportError:
            pass
    bases.append(graphene.ObjectType)
    return cast(
        graphene.ObjectType,
        type('Mutation', tuple(bases), {}),
    )


schema = graphene.Schema(query=_build_query(), mutation=_build_mutation())

