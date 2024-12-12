from django.urls import path
from floma_docs_api.consumers import DocumentConsumer

websocket_urlpatterns = [
    path('ws/documents/<document_id>/', DocumentConsumer.as_asgi()),
]