"""
URL configuration for floma_docs_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from floma_docs_api.views import CurrentUserView, DocumentView, InviteCollaboratorView

urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/user/', CurrentUserView.as_view()),
    path('api/documents/<int:document_id>/', DocumentView.as_view()),
    path('api/documents/<int:document_id>/invite/', InviteCollaboratorView.as_view(), name='invite-collaborator'),
    path('api/documents/', DocumentView.as_view(), name='document_list'),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
