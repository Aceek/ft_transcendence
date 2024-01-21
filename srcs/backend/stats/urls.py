from django.urls import path, include
from .views import StatsView, MatchHistoryView, MatchHistoryViewById


urlpatterns = [
    # Stats view
    path("stats/me", StatsView.as_view(), name="stats"),
    path("stats/<uuid:user_id>", StatsView.as_view(), name="stats_by_user_id"),
    # Match history view
    path("history/me", MatchHistoryView.as_view(), name="history"),
    path(
        "history/<uuid:user_id>",
        MatchHistoryViewById.as_view(),
        name="history_by_user_id",
    ),
]
