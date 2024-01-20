from django.shortcuts import render
from .models import Stats
from .serializers import StatsSerializer
from rest_framework import viewsets
from rest_framework import mixins

# Create your views here.

class StatsView(mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Stats.objects.all()
    serializer_class = StatsSerializer
