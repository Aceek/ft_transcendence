from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from .models import Tournament
from .serializers import TournamentSerializer
from CustomUser.models import CustomUser
from rest_framework.pagination import PageNumberPagination
from stats.views import CustomPageNumberPagination
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from .manageTournament import ManageTournament
from rest_framework import serializers

# Create your views here.


class TournamentView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TournamentSerializer
    pagination_class = CustomPageNumberPagination

    def perform_create(self, serializer):
        count = Tournament.objects.filter(
            ownerUser=self.request.user, is_finished=False
        ).count()
        if count >= 5:
            message = "You can't create more than 5 active tournaments (that's are not finished)"
            raise serializers.ValidationError(message)
        tournament = serializer.save(ownerUser=self.request.user)

        # Ajoute automatiquement l'utilisateur comme participant du tournoi
        tournament.user.add(self.request.user)
        tournament.save()

    def get_queryset(self):
        return Tournament.objects.get_queryset().order_by("-created_at")


class TournamentJoinView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, uid):
        tournament = get_object_or_404(Tournament, uid=uid)
        user = request.user

        # Vérifier si le tournoi est plein
        if tournament.user.count() >= tournament.max_participants:
            return Response(
                {"message": "Tournament is full"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Vérifier si l'utilisateur a déjà rejoint le tournoi
        if tournament.user.filter(id=user.id).exists():
            return Response(
                {"message": "User already joined the tournament"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if tournament.is_active:
            return Response(
                {"message": "Tournament is already active"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user.tournament.filter(is_finished=False).count() >= 5:
            return Response(
                {"message": "User is already in 5 active tournaments"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Ajouter l'utilisateur au tournoi
        tournament.user.add(user)
        tournament.save()
        # modifier le nombre de places restantes
        tournament.place_left = tournament.max_participants - tournament.user.count()
        tournament.save()
        return Response(
            {"message": "User joined the tournament"}, status=status.HTTP_200_OK
        )
    

    def delete(self, request, uid):
        tournament = get_object_or_404(Tournament, uid=uid)
        user = request.user

        # Vérifier si l'utilisateur est dans le tournoi
        if not tournament.user.filter(id=user.id).exists():
            return Response(
                {"message": "User not in the tournament"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Empêcher de quitter un tournoi actif
        if tournament.is_active:
            return Response(
                {"message": "Can't leave tournament while it's active"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if tournament.is_finished:
            return Response(
                {"message": "Can't leave tournament while it's finished"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        if tournament.ownerUser == user:
            return Response(
                {"message": "Can't leave tournament while you are the owner"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Retirer l'utilisateur du tournoi
        tournament.user.remove(user)
        tournament.save()
        # modifier le nombre de places restantes
        tournament.place_left = tournament.max_participants - tournament.user.count()
        tournament.save()
        return Response(
            {"message": "User left the tournament"}, status=status.HTTP_200_OK
        )


class TournamentLaunchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, uid):
        tournament = get_object_or_404(Tournament, uid=uid)
        user = request.user

        # Vérifier si l'utilisateur est le propriétaire du tournoi
        if tournament.ownerUser != user:
            return Response(
                {"message": "User is not the owner of the tournament"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Vérifier si le tournoi est plein
        if tournament.user.count() < 2:
            return Response(
                {"message": "Tournament is not full need at least 2 users"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if tournament.is_active:
            return Response(
                {"message": "Tournament is already active"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if tournament.is_finished:
            return Response(
                {"message": "Tournament is already finished"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        tournament.is_active = True
        # manageTournament(tournament)
        manageTournament = ManageTournament(tournament)
        manageTournament.organize_matches()
        tournament.save()
        return Response(
            {"message": "Tournament is now active"}, status=status.HTTP_200_OK
        )


# get tournament by id
class TournamentDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TournamentSerializer
    queryset = Tournament.objects.all()
    lookup_field = "uid"
    lookup_url_kwarg = "uid"


# get tournament by authenticated user
class UserTournamentView(generics.ListAPIView):
    """
    return all tournament that is not finished for the authenticated user
    """

    permission_classes = [IsAuthenticated]
    serializer_class = TournamentSerializer

    def get_queryset(self):
        # return Tournament.objects.filter(user=self.request.user).order_by("-created_at")
        return Tournament.objects.filter(
            user=self.request.user, is_finished=False
        ).order_by("-created_at")

# get tournament owner by authenticated user
class UserTournamentOwnerView(generics.ListAPIView):
    """
    return all tournament that is not finished for the authenticated user
    """

    permission_classes = [IsAuthenticated]
    serializer_class = TournamentSerializer

    def get_queryset(self):
        return Tournament.objects.filter(
            ownerUser=self.request.user, is_finished=False
        ).order_by("-created_at")
    

# delete tournament by id if the authenticated user is the owner
class TournamentDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TournamentSerializer
    queryset = Tournament.objects.all()
    lookup_field = "uid"
    lookup_url_kwarg = "uid"

    def perform_destroy(self, instance):
        if instance.ownerUser != self.request.user:
            raise serializers.ValidationError("You are not the owner of the tournament")
        if instance.is_finished:
            raise serializers.ValidationError("You can't delete a finished tournament")
        instance.delete()
        return Response(
            {"message": "Tournament deleted"}, status=status.HTTP_200_OK
        )

  
class TournamentHistoryView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TournamentSerializer

    def get_queryset(self):
        return Tournament.objects.filter(
            user=self.request.user, is_finished=True
        ).order_by("-created_at")