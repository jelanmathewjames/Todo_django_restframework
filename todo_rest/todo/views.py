from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import (CreateModelMixin,
                                   RetrieveModelMixin,
                                   UpdateModelMixin,
                                   DestroyModelMixin,
                                   ListModelMixin)
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status

from django.db.models import Case, When, Value, CharField

from pytz import timezone
from datetime import datetime

from authentication.auth import JWTAuthentication
from .serializers import TodoSerializer
from .models import Todo
# Create your views here.


class TodoViewSet(GenericViewSet, 
                  ListModelMixin, 
                  CreateModelMixin,
                  RetrieveModelMixin,
                  DestroyModelMixin,
                  UpdateModelMixin):
    
    authentication_classes = [JWTAuthentication]
    serializer_class = TodoSerializer
    pagination_class = PageNumberPagination

    def base_filter(self, data, flag):
        if not flag:
            pass

        elif flag == "completed":
            data = data.filter(
                is_completed=True
            ).all()

        elif flag == "pending":
            data = data.filter(
                is_completed=False,
                expiry__gte=datetime.now()
            ).all()

        elif flag == "expired":
            data = data.filter(
                is_completed=False,
                expiry__lt=datetime.now()
            ).all()

        return data
    
    def get_queryset(self):

        flag = self.request.query_params.get('flag', None)
        zone = timezone('Asia/Kolkata')
        user = self.request.user['user_id']
        data = Todo.objects.filter(user=user).all()
        data = data.annotate(status=Case(
            When(is_completed=True, then=Value("completed")),
            When(expiry__lt=datetime.now(zone), then=Value("expired")),
            When(expiry__gte=datetime.now(zone), then=Value("pending")),
            output_field=CharField()
        ))
        return self.base_filter(data, flag)

    @action(methods=['POST'], detail=False)
    def markall(self, request):
        user = request.user['user_id']
        ids = request.data.get('ids', [])
        if len(ids) <= 0:
            Todo.objects.filter(
                is_completed=False, 
                user=user, 
                expiry__gte=datetime.now()
            ).all().update(is_completed=True)
        else:
            Todo.objects.filter(
                is_completed=False, 
                user=user, 
                expiry__gte=datetime.now(),
                id__in=ids
            ).all().update(is_completed=True)
        return Response(
            {"code": 200, "message": "Marked as completed"}, 
            status=status.HTTP_200_OK)
    
    @action(methods=['POST'], detail=False)
    def delete(self, request):
        user = request.user['user_id']
        ids = request.data.get('ids', [])
        flag = request.data.get('flag', None)
        data = Todo.objects.filter(user=user)
        
        if len(ids) <= 0:
            data = self.base_filter(data, flag)
            data.delete()
        else:
            data.filter(id__in=ids).delete()
        
        return Response(
            {"code": 200, "message": "Marked as completed"}, 
            status=status.HTTP_200_OK)
        