from django.urls import path
from .consumers import *

user_websocket_urlpatterns = [
  path('user/notification/' , UserNotificationConsumer.as_asgi()),
]