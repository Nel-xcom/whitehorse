from django.urls import path
from core.consumers import ChatConsumer

websocket_urlpatterns = [
    path('ws/chat/<int:usuario_id>/', ChatConsumer.as_asgi()),
]
