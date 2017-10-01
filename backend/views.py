from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from django.contrib.admin.views.decorators import staff_member_required
from django.http import (
    HttpRequest,
    HttpResponse,
)
from graphene_django.views import GraphQLView
from graphql.execution.executors.asyncio import AsyncioExecutor
from rest_auth.registration.views import SocialLoginView
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.settings import api_settings

import asyncio


class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter


@api_view(['GET', 'POST'])
@authentication_classes(api_settings.DEFAULT_AUTHENTICATION_CLASSES)
@permission_classes((IsAuthenticated,))
def graphql(request: HttpRequest) -> HttpResponse:
    view = GraphQLView.as_view(
        graphiql=False,
        executor=AsyncioExecutor(loop=asyncio.get_event_loop()),
    )
    return view(request.data)


@staff_member_required
def graphiql(request: HttpRequest) -> HttpResponse:
    view = GraphQLView.as_view(
        graphiql=True,
        executor=AsyncioExecutor(loop=asyncio.get_event_loop()),
    )
    return view(request)

