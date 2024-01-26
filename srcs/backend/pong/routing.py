# routing.py
# from channels.routing import ProtocolTypeRouter, URLRouter
# from django.urls import re_path
# from .consumers import GameConsumer

# websocket_urlpatterns = [
#     re_path(r'ws/pong/$', GameConsumer.as_asgi()),
#     # Add more paths for different WebSocket consumers if needed
# ]

# application = ProtocolTypeRouter(
#     {
#         "websocket": URLRouter(websocket_urlpatterns),
#         # Add other protocols if needed (e.g., http)
#     }
# )
