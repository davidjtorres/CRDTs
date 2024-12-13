from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from floma_docs_api.models import Document
from floma_docs_api.serializers import DocumentSerializer, InviteCollaboratorSerializer


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"id": request.user.id, "username": request.user.username})


class DocumentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, document_id=None):
        if document_id:
            document = Document.objects.get(Q(id=document_id) & (Q(owner=request.user) | Q(collaborators=request.user)))
            serializer = DocumentSerializer(document)
            return Response(serializer.data)
        else:
            documents = Document.objects.filter(Q(owner=request.user) | Q(collaborators=request.user)).distinct()
            serializer = DocumentSerializer(documents, many=True)
            return Response(serializer.data)

    def post(self, request):
        serializer = DocumentSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, document_id):
        document = Document.objects.get(Q(id=document_id) & (Q(owner=request.user) | Q(collaborators=request.user)))
        serializer = DocumentSerializer(document, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InviteCollaboratorView(APIView):
    def post(self, request, document_id):
        data = request.data.copy()
        data['document_id'] = document_id
        serializer = InviteCollaboratorSerializer(data=data)
        if serializer.is_valid():
            document = serializer.validated_data['document']
            user = serializer.validated_data['user']
            document.collaborators.add(user)
            document.save()
            return Response({"message": "User invited as collaborator"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)