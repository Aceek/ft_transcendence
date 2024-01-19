from django.shortcuts import render

# Create your views here.

class StatsView(APIView):
    def get(self, request):
        return Response({"message": "Hello, world!"})