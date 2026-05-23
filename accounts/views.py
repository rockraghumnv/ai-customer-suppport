from django.contrib.auth import get_user_model
from rest_framework import permissions, status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import RegisterSerializer, LoginSerializer


User = get_user_model()


class RegisterView(GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        refresh["company_id"] = user.company_id
        access = refresh.access_token
        access["company_id"] = user.company_id
        return Response(
            {
                "refresh": str(refresh),
                "access": str(access),
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "company": user.company_id,
                },
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)
        refresh["company_id"] = user.company_id
        access = refresh.access_token
        access["company_id"] = user.company_id
        return Response(
            {
                "refresh": str(refresh),
                "access": str(access),
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "company": user.company_id,
                },
            },
            status=status.HTTP_200_OK,
        )
