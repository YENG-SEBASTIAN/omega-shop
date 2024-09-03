from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.serializers import UserRegisterSerializer, UserLoginSerializer
from accounts.models import User

class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        refresh = RefreshToken.for_user(self.request.user)
        return Response(
            status=status.HTTP_201_CREATED,
        )

class UserLoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password']
        )
        if user:
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                status=status.HTTP_200_OK,
            )
        return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
