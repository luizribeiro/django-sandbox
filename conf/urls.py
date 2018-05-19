from django.contrib import admin
from django.conf.urls import (
    include,
    url,
)

import backend.views

admin.autodiscover()

urlpatterns = [
    url(r'^graphql/$', backend.views.graphql, name='graphql'),
    url(r'^graphiql/$', backend.views.graphiql, name='graphiql'),

    url(r'^accounts/', include('allauth.socialaccount.urls')),
    url(r'^api/auth/', include('rest_auth.urls')),
    url(r'^api/registration/', include('rest_auth.registration.urls')),
    url(r'^api/auth/facebook/$', backend.views.FacebookLogin.as_view(), name='fb_login'),

    url(r'^admin/', admin.site.urls),
]

