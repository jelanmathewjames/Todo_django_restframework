from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from authentication.auth import jwt_generator
from authentication.auth import JWTAuthentication
from user.models import Token
# Create your views here.


class UserViewSet(ViewSet):
    authentication_classes = [JWTAuthentication]
    http_method_names = ["post"]

    @action(methods=['POST'], detail=False, authentication_classes=[])
    def login(self, request):

        username = request.data.get('username', None)
        password = request.data.get('password', None)
        user = authenticate(username=username, password=password)

        if not user:
            return Response(
                {"code": 414,
                 "message": "Login Failed"},
                status=status.HTTP_412_PRECONDITION_FAILED,
            )

        access_token = jwt_generator(
            user.id,
        )
        token = Token.objects.filter(user=user)
        if token.exists():
            token.update(token=access_token, is_expired=False)
        else:
            Token.objects.create(
                user=user,
                token=access_token
            )
        return Response(
            {"code": 200,
             "message": "Login successful",
             "access_token": access_token},
            status=status.HTTP_200_OK,
        )

    @action(methods=['POST'], detail=False, authentication_classes=[])
    def signup(self, request):

        username = request.data.get('username', None)
        password = request.data.get('password', None)
        first_name = request.data.get('first_name', None)
        last_name = request.data.get('last_name', None)

        if username is None or password is None or first_name is None or last_name is None:
            return Response({"code": 412, "message": "Required fields are missing"},
                            status=status.HTTP_412_PRECONDITION_FAILED,)

        User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        return Response({"code": 201, "message": "User created successfully"},
                        status=status.HTTP_201_CREATED,)

    @action(methods=['POST'], detail=False)
    def logout(self, request):
        token = request.headers.get("Authorization", "")
        Token.objects.filter(token=token).update(is_expired=True)
        return Response(
            {"code": 200, "message": "Logout successful"},
            status=status.HTTP_200_OK,
        )
