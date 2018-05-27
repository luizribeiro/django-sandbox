from django.urls import path

import rosie.views

urlpatterns = [
    path('', rosie.views.webhook),
]

