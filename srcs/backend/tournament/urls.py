from django.urls import path
from .views import (
    TournamentView,
    TournamentJoinView,
    TournamentLaunchView,
    TournamentDetailView,
    UserTournamentView,
    UserTournamentOwnerView,
    TournamentDeleteView,
    TournamentHistoryView,
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
    path(
        "tournaments/me",
        UserTournamentView.as_view(),
        name="tournaments-user",
    ),
    # UserTournamentOwnerView
    path(
        "tournaments/me/owned",
        UserTournamentOwnerView.as_view(),
        name="tournaments-owner",
    ),
    path(
        "tournaments/<uuid:uid>/delete",
        TournamentDeleteView.as_view(),
        name="tournaments-delete",
    ),
    path(
        "tournaments/history",
        TournamentHistoryView.as_view(),
        name="tournaments-history",
    ),
]
