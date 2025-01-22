import redis
from channels.generic.websocket import AsyncWebsocketConsumer
from y_py import YDoc, apply_update, encode_state_as_update
import logging
from .models import Document
from django.conf import settings
import jwt


logger = logging.getLogger(__name__)


class DocumentConsumer(AsyncWebsocketConsumer):
    async def connect(self):

        logger.info("connection")
        self.document_id = self.scope["url_route"]["kwargs"]["document_id"]
        self.room_group_name = f"document_{self.document_id}"

        # Validate connection
        if not await self.validate_connection():
            await self.close()
            return

        # Join room group
        logger.info(f"Connected {self.channel_name}")
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        # Initialize Redis connection
        try:
            self.redis_client = redis.StrictRedis(host="redis", port=6379)
        except redis.ConnectionError as e:
            logger.error(f"Error saving document to database: {e}")
            return
        try:

            # Initialize YDoc and YText
            self.ydoc = YDoc()
            self.ytext = self.ydoc.get_text("content")

            # Load document state from Redis
            state = await self.get_document_state()
            if state:
                apply_update(self.ydoc, state)
                logger.info(
                    f"Document state loaded from Redis {self.ydoc.get_text('content')}"
                )

            # Accept the WebSocket connection
            await self.accept()  # Assuming state is the initial content

            await self.send(bytes_data=encode_state_as_update(self.ydoc))
        except Exception as e:
            logger.error(f"Error initializing YDoc: {e}")
            await self.close()

    async def disconnect(self, close_code):

        content = str(self.ydoc.get_text("content"))
        b_content = encode_state_as_update(self.ydoc)
        await self.save_document_content_to_db(content=content, b_content=b_content)
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, bytes_data):
        # data = json.loads(text_data)
        update = bytes_data

        # Apply the update to the YDoc
        apply_update(self.ydoc, update)

        # Encode the state
        state = encode_state_as_update(self.ydoc)

        # Save changes to Redis
        await self.save_document_state(state)

        logger.info(f"receiving message from {self.channel_name}")

        # Broadcast changes to group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "document_update",
                "changes": update,
                "sender_channel_name": self.channel_name,
            },
        )

    async def document_update(self, event):
        changes = event["changes"]
        sender_channel_name = event["sender_channel_name"]

        # Skip sending the message back to the sender
        if self.channel_name != sender_channel_name:
            logger.info(f"Sending changes to {self.channel_name}")
            await self.send(bytes_data=changes)

    async def get_document_state(self):
        # Get the document content from redis or the database
        try:
            state = self.redis_client.get(f"document_state_{self.document_id}")
            if state:
                logger.info("Document state found in Redis")
                return state
            else:
                try:
                    logger.info("Document state found in DB")
                    document = await Document.objects.aget(id=self.document_id)
                    # Save the document content to Redis
                    self.redis_client.set(
                        f"document_state_{self.document_id}", document.b_content
                    )
                    return document.b_content
                except Document.DoesNotExist:
                    logger.error("Document not found in database")
                    return None

        except Exception as e:
            logger.error(f"Error getting document state from Redis/DB: {e}")
            return None

    async def save_document_state(self, state):
        try:
            self.redis_client.set(f"document_state_{self.document_id}", state)
        except Exception as e:
            logger.error(f"Error saving document state to Redis: {e}")

    async def save_document_content_to_db(self, content, b_content):
        logger.info("Saving document to database")
        try:
            # Save the document content to the database
            await Document.objects.aupdate_or_create(
                id=self.document_id,
                defaults={"content": content, "b_content": b_content},
            )
            logger.info(f"Document {self.document_id} saved to database")
        except Exception as e:
            logger.error(f"Error saving document to database: {e}")

    async def validate_connection(self):
        # Extract token from query parameters
        token = self.scope["query_string"].decode().split("=")[1]

        # Validate token
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            self.user_id = payload["user_id"]
        except jwt.ExpiredSignatureError:
            logger.error("Token has expired")
            return False
        except jwt.InvalidTokenError:
            logger.error("Invalid token")
            return False

        # Check if user has access to the document
        has_access = await self.user_has_access()
        if not has_access:
            logger.error("User does not have access to the document")
            return False

        return True

    async def user_has_access(self):
        # validate if user has access to the document
        try:
            document = await Document.objects.aget(id=self.document_id)
            if document.owner_id == self.user_id:
                return True
            if await document.collaborators.filter(id=self.user_id).aexists():
                return True
        except Document.DoesNotExist:
            return False
        return False
