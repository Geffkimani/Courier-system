from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import courier.routing

application = ProtocolTypeRouter({
    "http":
        __import__("django.core.asgi").core.asgi.get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            courier.routing.websocket_urlpatterns
        )
    ),
})
