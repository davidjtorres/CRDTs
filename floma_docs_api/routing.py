from django.urls import path
from FlomaDocs.consumers import DocumentConsumer

websocket_urlpatterns = [
    path('ws/documents/<document_id>/', DocumentConsumer.as_asgi()),
]