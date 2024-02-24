from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from .serializers import TwoFactorValidateSerializer, VerifyEmailSerializer


class TwoFactorVerifyView(APIView):
    permission_classes = [AllowAny]
    serializer_class = TwoFactorValidateSerializer

    def post(self, request):
        serializer = TwoFactorValidateSerializer(data=request.data)
        if serializer.is_valid():
            response = Response(status=status.HTTP_200_OK)
            data = serializer.save()
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


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]
    serializer_class = VerifyEmailSerializer

    def get(self, request, *args, **kwargs):
        serializer = VerifyEmailSerializer(data=request.GET)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    "detail": f"User {user.get_username()} has been successfully activated."
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
