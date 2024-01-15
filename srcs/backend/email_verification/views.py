from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
# from .serializers import VerifyEmailSerializer


# class SendVerificationEmailView(APIView):
    # def get(self, request, *args, **kwargs):
    #     serializer = VerifyEmailSerializer(data=request.GET)
    #     if serializer.is_valid():
    #         serializer.send_mail()
    #         return Response(status=status.HTTP_200_OK)
