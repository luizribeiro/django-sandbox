from django.http import HttpResponse
from django.shortcuts import render
from nest import Nest
from os import environ as env


def nest(request):
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


def react(request):
    return render(request, 'index.html')

