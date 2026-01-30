from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WebhookView, ProjectViewSet

router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')

urlpatterns = [
    path('', include(router.urls)),
    path('webhook/commit/', WebhookView.as_view(), name='webhook_commit'),
]
