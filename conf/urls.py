from django.conf.urls import url

import backend.views

urlpatterns = [
    url(r'^$', backend.views.nest, name='nest'),
    url(r'^react$', backend.views.react, name='react'),
    url(r'^graphql/$', backend.views.graphiql, name='graphql'),
    url(r'^graphiql/$', backend.views.graphiql, name='graphiql'),
]

