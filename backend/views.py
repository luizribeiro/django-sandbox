from django.http import (
    HttpRequest,
    HttpResponse,
)
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView
from graphql.execution.executors.asyncio import AsyncioExecutor
import asyncio


@csrf_exempt
def graphql(request: HttpRequest) -> HttpResponse:
    view = GraphQLView.as_view(
        graphiql=False,
        executor=AsyncioExecutor(loop=asyncio.get_event_loop()),
    )
    return view(request)


def graphiql(request: HttpRequest) -> HttpResponse:
    view = GraphQLView.as_view(
        graphiql=True,
        executor=AsyncioExecutor(loop=asyncio.get_event_loop()),
    )
    return view(request)

