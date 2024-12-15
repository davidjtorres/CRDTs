import redis
from channels.generic.websocket import AsyncWebsocketConsumer
from y_py import YDoc, apply_update, encode_state_as_update
from asgiref.sync import sync_to_async
import logging
from .models import Document
from django.conf import settings
import jwt


logger = logging.getLogger(__name__)


class DocumentConsumer(AsyncWebsocketConsumer):
    async def connect(self):

        logger.info("Connected")
        self.document_id = self.scope["url_route"]["kwargs"]["document_id"]
        self.room_group_name = f"document_{self.document_id}"

        # Validate connection
        if not await self.validate_connection():
            await self.close()
            return

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        # Initialize Redis connection
        try:
            self.redis_client = redis.StrictRedis(host="redis", port=6379)
        except redis.ConnectionError as e:
            logger.error(f"Error saving document to database: {e}")
            return

        # Initialize YDoc and YText
        self.ydoc = YDoc()
        self.ytext = self.ydoc.get_text("content")

        # Load document state from Redis
        state = await self.get_document_state()
        if state:
            apply_update(self.ydoc, state)

        # Accept the WebSocket connection
        await self.accept()  # Assuming state is the initial content

        await self.send(bytes_data=encode_state_as_update(self.ydoc))

    async def disconnect(self, close_code):

        content = str(self.ydoc.get_text("content"))
        b_content = encode_state_as_update(self.ydoc)
        await self.save_document_content_to_db(content=content, b_content=b_content)
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, bytes_data):
        # data = json.loads(text_data)
        update = bytes_data

        # size of the update
        logger.info(f"Received update of size {len(update)}")

        # Apply the update to the YDoc
        apply_update(self.ydoc, update)

        # Encode the state
        state = encode_state_as_update(self.ydoc)

        # Save changes to Redis
        await self.save_document_state(state)

        # Broadcast changes to group
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "document_update", "changes": update}
        )

    async def document_update(self, event):
        changes = event["changes"]

        # Send changes to WebSocket
        await self.send(bytes_data=changes)

    @sync_to_async
    def get_document_state(self):
        # Get the document content from redis or the database
        try:
            state = self.redis_client.get(f"document_state_{self.document_id}")
            if state:
                logger.info("Document state found in Redis")
                return state
            else:
                try:
                    logger.info("Document state found in DB")
                    document = Document.objects.get(id=self.document_id)
                    # Save the document content to Redis
                    self.redis_client.set(f"document_state_{self.document_id}", document.b_content)
                    return document.b_content
                except Document.DoesNotExist:
                    return None

        except Exception as e:
            logger.error(f"Error getting document state from Redis/DB: {e}")
            return None

    async def save_document_state(self, state):
        try:
            self.redis_client.set(f"document_state_{self.document_id}", state)
        except Exception as e:
            logger.error(e)

    @sync_to_async
    def save_document_content_to_db(self, content, b_content):
        logger.info("Saving document to database")
        try:
            # Save the document content to the database
            Document.objects.update_or_create(
                id=self.document_id,
                defaults={"content": content, "b_content": b_content},
            )
            logger.info(f"Document {self.document_id} saved to database")
        except Exception as e:
            logger.error(f"Error saving document to database: {e}")

    async def validate_connection(self):
        # Extract token from query parameters
        token = self.scope["query_string"].decode().split("=")[1]
        logger.info(f"Token: {token}")

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

    @sync_to_async
    def user_has_access(self):
        #validate if user has access to the document
        try:
            document = Document.objects.get(id=self.document_id)
            if document.owner_id == self.user_id:
                return True
            if document.collaborators.filter(id=self.user_id).exists():
                return True
        except Document.DoesNotExist:
            return False
        return False
