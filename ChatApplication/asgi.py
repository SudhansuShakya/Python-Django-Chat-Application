"""
ASGI config for ChatApplication project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
from django.urls import path, re_path, include
from django.core.asgi import get_asgi_application
from channels.routing import get_default_application,ProtocolTypeRouter
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter , URLRouter
from Chat.consumers import NotificationConsumer
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ChatApplication.settings')

application = ProtocolTypeRouter(
    {
        "http" : get_asgi_application() , 
        "websocket" : AuthMiddlewareStack(
            URLRouter([
                path('ws/notifications/<str:user_id>/',NotificationConsumer.as_asgi()),
            ]
            )    
        )
    }
)
