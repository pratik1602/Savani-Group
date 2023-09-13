from django.urls import path
from .consumers import *

websocket_urlpatterns = [
  path('admin/notification/' , AdminNotificationConsumers.as_asgi()),
]


# ws://localhost:8000/ws/sc/ unsecure connection
# wss://localhost:8000/ws/sc/ secure connection