from rest_framework.routers import DefaultRouter
from .views import TodoViewSet
from django.urls import path, include

router = DefaultRouter(trailing_slash=False)
router.register('', TodoViewSet, basename='todos')

urlpatterns = [
    path(r"", include(router.urls)),
]