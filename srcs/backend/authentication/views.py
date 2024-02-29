from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from .serializers import (
    OAuth42Serializer,
    RegisterSerializer,
    LoginSerializer,
)


class RegisterView(APIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            response = Response(status=status.HTTP_200_OK)
            if '2FA' in data:
                response.data = data
            else:
                response.set_cookie(
                    "access_token",
                    data["access"],
                    httponly=True,
                    samesite="strict",
                    secure=True,
                )
                response.set_cookie(
                    "refresh_token",
                    data["refresh"],
                    httponly=True,
                    samesite="strict",
                    secure=True,
                )
            return response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    http_method_names = ["get"]

    def get(self, request, *args, **kwargs):
        token = request.COOKIES.get("refresh_token")
        if token is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            RefreshToken(token).blacklist()
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.set_cookie(
                    "access_token",
                    "None",
                    httponly=True,
                    samesite="none",
                    secure=True,
        )
        response.set_cookie(
                    "refresh_token",
                    "None",
                    httponly=True,
                    samesite="none",
                    secure=True,
        )
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return response


class TokenRefreshView(APIView):
    permission_classes = [AllowAny]
    http_method_names = ["get"]

    def get(self, request, *args, **kwargs):
        refresh = request.COOKIES.get("refresh_token")
        if  refresh is not None:
            serializer = TokenRefreshSerializer(
                data={"refresh": request.COOKIES.get("refresh_token")}
            )
            if serializer.is_valid(raise_exception=True):
                data = serializer.validated_data
                response = Response(status=status.HTTP_200_OK)
                response.set_cookie(
                    "access_token",
                    data["access"],
                    httponly=True,
                    samesite="strict",
                    secure=True,
                )
                return response
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

class OAuth42View(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        serializer = OAuth42Serializer(data=request.GET)
        if serializer.is_valid():
            return self.handle_valid_serializer(serializer)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def handle_valid_serializer(self, serializer):
        data = serializer.validated_data
        if "access" in data and "refresh" in data:
            return self.create_token_response(data)
        return Response(data, status=status.HTTP_200_OK)

    def create_token_response(self, data):
        response = Response(status=status.HTTP_200_OK)
        response.set_cookie(
            "access_token",
            data["access"],
            httponly=True,
            samesite="strict",
            secure=True,
        )
        response.set_cookie(
            "refresh_token",
            data["refresh"],
            httponly=True,
            samesite="strict",
            secure=True,
        )
        return response


class PingView(APIView):
    permission_classes = [IsAuthenticated]
    http_method_names = ["get"]

    def get(self, request):
        return Response(status=status.HTTP_200_OK)
