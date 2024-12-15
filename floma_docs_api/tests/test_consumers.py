from channels.testing import WebsocketCommunicator
from django.test import TransactionTestCase
from floma_docs_api.models import Document, User
from floma_docs_api.asgi import application
from unittest.mock import AsyncMock, patch
from y_py import YDoc, encode_state_as_update


class DocumentConsumerTest(TransactionTestCase):

    # setup create document
    def setUp(self):
        user = User.objects.create_user(username="testuser", password="12345")
        Document.objects.create(
            title="Test Document", content="Test Content", owner=user
        )

    async def test_connect_sokcet(self):

        # Mock the validate_connection method
        with patch.multiple(
            "floma_docs_api.consumers.DocumentConsumer",
            validate_connection=AsyncMock(return_value=True),
        ):
            communicator = WebsocketCommunicator(application, "/ws/documents/1/")
            connected, subprotocol = await communicator.connect()
            self.assertTrue(connected)

        await communicator.disconnect()

    async def test_send_message(self):
        # Mock the validate_connection method
        with patch(
            "floma_docs_api.consumers.DocumentConsumer.validate_connection",
            AsyncMock(return_value=True),
        ), patch("floma_docs_api.consumers.apply_update", AsyncMock(return_value=None)):
            communicator = WebsocketCommunicator(application, "/ws/documents/1/")
            connected, subprotocol = await communicator.connect()
            self.assertTrue(connected)
            # send bytes
            # Encode bytes data as base64 string
            b_content = encode_state_as_update(YDoc())
            await communicator.send_to(bytes_data=b_content)

        await communicator.disconnect()
