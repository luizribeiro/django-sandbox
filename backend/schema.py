from django.conf import settings
from importlib import import_module
import graphene


def _build_query() -> graphene.ObjectType:
    bases = []
    for app in settings.INSTALLED_APPS:
        try:
            queries = import_module('.queries', app)
            bases.append(queries.Query)  # type: ignore
        except ImportError:
            pass
        except AttributeError:
            pass
    bases.append(graphene.ObjectType)
    return type('Query', tuple(bases), {})


schema = graphene.Schema(query=_build_query())

