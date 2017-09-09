from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView
from graphql.execution.executors.asyncio import AsyncioExecutor

import backend.views

urlpatterns = [
    url(r'^$', backend.views.nest, name='nest'),
    url(r'^react$', backend.views.react, name='react'),
    url(r'^graphql/$', csrf_exempt(GraphQLView.as_view(graphiql=False, executor=AsyncioExecutor())), name='graphql'),
    url(r'^graphiql/$', GraphQLView.as_view(graphiql=True, executor=AsyncioExecutor()), name='graphiql'),
]

