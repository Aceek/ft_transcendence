from django.urls import path, include
from rest_framework import routers
from .views import StatsView, MatchHistoryView

router = routers.DefaultRouter()
router.register(r"stats", StatsView)
router.register(r"match_history", MatchHistoryView, basename="MatchHistory")

urlpatterns = [
    path("", include(router.urls)),
]
