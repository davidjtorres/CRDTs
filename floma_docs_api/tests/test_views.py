from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from floma_docs_api.models import Document


class CurrentUserViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_current_user(self):
        url = reverse("current-user")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "testuser")


class DocumentViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.document = Document.objects.create(
            title="Test Document", content="Test Content", owner=self.user
        )

    def test_get_documents(self):
        url = reverse("document-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Test Document")

    def test_get_single_document(self):
        url = reverse("document-detail", args=[self.document.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Test Document")

    def test_create_document(self):
        url = reverse("document-list")
        data = {"title": "New Document", "content": "New Content"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Document.objects.count(), 2)
        self.assertEqual(
            Document.objects.get(id=response.data["id"]).title, "New Document"
        )

    def test_update_document(self):
        url = reverse("document-detail", args=[self.document.id])
        data = {"title": "Updated Document", "content": "Updated Content"}
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.document.refresh_from_db()
        self.assertEqual(self.document.title, "Updated Document")

    def test_get_documents_unauthenticated(self):
        self.client.logout()
        url = reverse("document-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_document_unauthenticated(self):
        self.client.logout()
        url = reverse("document-list")
        data = {"title": "New Document", "content": "New Content"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
