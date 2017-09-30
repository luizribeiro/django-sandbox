from django.conf.urls import url

import backend.views
import home.views

urlpatterns = [
    url(r'^$', home.views.nest, name='nest'),
    url(r'^react$', home.views.react, name='react'),
    url(r'^graphql/$', backend.views.graphql, name='graphql'),
    url(r'^graphiql/$', backend.views.graphiql, name='graphiql'),
]

