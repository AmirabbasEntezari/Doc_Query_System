from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DocumentViewSet, ChatSessionViewSet

router = DefaultRouter()
router.register(r'documents', DocumentViewSet, basename='document')
router.register(r'history', ChatSessionViewSet, basename='history')

urlpatterns = [
    path('', include(router.urls)),
]