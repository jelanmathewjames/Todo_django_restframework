from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'', UserViewSet, basename='todo')

urlpatterns = [
    path(r'', include(router.urls)),
]