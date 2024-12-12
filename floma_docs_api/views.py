from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from floma_docs_api.models import Document
from floma_docs_api.serializers import DocumentSerializer


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
        serializer = DocumentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def put(self, request, document_id):
        document = Document.objects.get(Q(id=document_id) & (Q(owner=request.user) | Q(collaborators=request.user)))
        serializer = DocumentSerializer(document, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
