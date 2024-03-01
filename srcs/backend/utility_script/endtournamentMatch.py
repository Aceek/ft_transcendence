from tournament.models import Tournament
from tournament.models import Matches
from tournament.manageTournament import ManageTournament
from CustomUser.models import CustomUser
import random

# Remplacez 'your_tournament_uid' par l'UID de votre tournoi
tournament_uid = '54a8985d-5126-4522-a9ed-b7e53ca35437'
tournament = Tournament.objects.get(uid=tournament_uid)

# Instanciez votre gestionnaire de tournoi
manager = ManageTournament(tournament)

# Récupérez tous les matchs actifs pour le tournoi
active_matches = Matches.objects.filter(tournament=tournament, is_active=True, is_finished=False)

for match in active_matches:
    # Choisissez aléatoirement un gagnant parmi les deux joueurs
    winner = random.choice([match.user1, match.user2])
    # Utilisez la méthode set_end_match pour terminer le match et désigner le gagnant
    manager.set_end_match(match, winner)

print("Tous les matchs actifs ont été terminés avec un gagnant aléatoire.")