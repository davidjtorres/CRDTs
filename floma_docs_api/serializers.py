from rest_framework import serializers
from django.utils import timezone
from django.contrib.auth.models import User
from .models import Document


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class DocumentSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    collaborators = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Document
        fields = [
            "id",
            "title",
            "content",
            "b_content",
            "owner",
            "collaborators",
            "created_at",
            "last_edited_at",
        ]
        read_only_fields = [
            "id",
            "owner",
            "collaborators",
            "created_at",
            "last_edited_at",
        ]

    def create(self, validated_data):
        request = self.context.get("request")
        document = Document.objects.create(
            title=validated_data["title"],
            owner=request.user,
            last_edited_at=timezone.now(),
        )
        return document

    def update(self, instance, validated_data):
        instance.title = validated_data.get("title", instance.title)
        instance.last_edited_at = timezone.now()
        instance.save()
        return instance


class InviteCollaboratorSerializer(serializers.Serializer):
    document_id = serializers.IntegerField()
    user_id = serializers.IntegerField(required=False)
    email = serializers.EmailField(required=False)

    def validate(self, data):
        try:
            data["document"] = Document.objects.get(id=data["document_id"])
        except Document.DoesNotExist:
            raise serializers.ValidationError("Document does not exist")

        if "user_id" in data:
            try:
                data["user"] = User.objects.get(id=data["user_id"])
            except User.DoesNotExist:
                raise serializers.ValidationError("User with this ID does not exist")
        elif "email" in data:
            try:
                data["user"] = User.objects.get(email=data["email"])
            except User.DoesNotExist:
                raise serializers.ValidationError("User with this email does not exist")
        else:
            raise serializers.ValidationError(
                "Either user_id or email must be provided"
            )

        return data
