from rest_framework import serializers
from FlomaDocs.models import Document


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = [
            "id",
            "title",
            "content",
            "owner",
            "collaborators",
            "created_at",
            "last_edited_at",
        ]
