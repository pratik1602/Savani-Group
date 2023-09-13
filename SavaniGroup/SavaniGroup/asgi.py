"""
ASGI config for SavaniGroup project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os

from channels.routing import ProtocolTypeRouter , URLRouter
from Notification.middlewares import TokenAuthMiddleWare
from django.core.asgi import get_asgi_application

from Notification.routing import websocket_urlpatterns
from users.routing import user_websocket_urlpatterns

from django.urls import re_path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SavaniGroup.settings')

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
  'http':django_asgi_app,
  'websocket':TokenAuthMiddleWare(
    URLRouter(
      websocket_urlpatterns +
      user_websocket_urlpatterns
    )
  )
})