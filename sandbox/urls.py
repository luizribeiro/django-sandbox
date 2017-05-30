from django.conf.urls import include, url

import hello.views

urlpatterns = [
    url(r'^$', hello.views.nest, name='nest'),
    url(r'^react$', hello.views.react, name='react'),
]
