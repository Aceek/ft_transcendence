from django.urls import path, include
from rest_framework import routers
from .views import StatsView

router = routers.DefaultRouter()
router.register(r"stats", StatsView)

urlpatterns = [
    path("", include(router.urls)),
]
