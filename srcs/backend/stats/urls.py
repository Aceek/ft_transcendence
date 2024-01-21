from django.urls import path, include
from rest_framework import routers
from .views import StatsView, MatchHistoryView

router = routers.DefaultRouter()
# router.register(r"stats", StatsView)
router.register(r"match_history", MatchHistoryView, basename="MatchHistory")

urlpatterns = [
    path("stats/me", StatsView.as_view(), name="stats"),
    path("stats/<uuid:user_id>", StatsView.as_view(), name="stats_by_user_id"),
    path("", include(router.urls)),
]
