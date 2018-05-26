from django.conf.urls import url

import rosie.views

urlpatterns = [
    url(r'^rosie/', rosie.views.receive_message),
]

