from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView

import hello.views

urlpatterns = [
    url(r'^$', hello.views.nest, name='nest'),
    url(r'^react$', hello.views.react, name='react'),
    url(r'^graphql/$', csrf_exempt(GraphQLView.as_view(graphiql=False)), name='graphql'),
    url(r'^graphiql/$', GraphQLView.as_view(graphiql=True), name='graphiql'),
]

