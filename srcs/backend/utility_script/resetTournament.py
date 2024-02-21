# reset script to reset the tournament

from tournament.models import Tournament
from tournament.models import Matches

# Remplacez 'your_tournament_uid' par l'UID de votre tournoi
tournament_uid = 'c0f15908-512e-4fa7-a917-1a532effae5e'
tournament = Tournament.objects.get(uid=tournament_uid)

# supprimez tous les matchs pour le tournoi
Matches.objects.filter(tournament=tournament).delete()

tournament.is_active = False
tournament.is_finished = False
tournament.round = 1
tournament.place_left = 8
tournament.winner = None
tournament.save()