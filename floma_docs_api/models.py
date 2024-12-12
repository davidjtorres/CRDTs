from django.db import models
from django.contrib.auth.models import User


class Document(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True)
    b_content = models.BinaryField(blank=True)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="owned_documents"
    )
    collaborators = models.ManyToManyField(
        User, related_name="collaborating_documents", blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    last_edited_at = models.DateTimeField()

    def __str__(self):
        return self.title
