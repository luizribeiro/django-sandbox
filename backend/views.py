from django.http import (
    HttpRequest,
    HttpResponse,
)
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView
from graphql.execution.executors.asyncio import AsyncioExecutor
from nest import Nest
from os import environ as env
import asyncio


def nest(request: HttpRequest) -> HttpResponse:
    nest = Nest(
        client_id=env.get('NEST_CLIENT_ID'),
        client_secret=env.get('NEST_CLIENT_SECRET'),
        access_token=env.get('NEST_ACCESS_TOKEN'),
    )
    thermostat = nest.thermostats[0]
    return HttpResponse(
        'Hello! The current temperature is {0:.1f}'.format(
            thermostat.temperature,
        ),
    )


def react(request: HttpRequest) -> HttpResponse:
    return render(request, 'index.html')


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

