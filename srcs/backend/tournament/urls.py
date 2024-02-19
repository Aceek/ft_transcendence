from django.urls import path
from .views import (
    TournamentView,
    TournamentJoinView,
    TournamentLaunchView,
    TournamentDetailView,
)

urlpatterns = [
    path("tournaments", TournamentView.as_view(), name="tournaments"),
    # view base on uid of tournament
    path(
        "tournaments/<uuid:uid>/join",
        TournamentJoinView.as_view(),
        name="tournaments-join",
    ),
    path(
        "tournaments/<uuid:uid>/launch",
        TournamentLaunchView.as_view(),
        name="tournaments-launch",
    ),
    path(
        "tournaments/<uuid:uid>/retrieve",
        TournamentDetailView.as_view(),
        name="tournaments-retrieve",
    ),
]
