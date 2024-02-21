from django.contrib.auth import get_user_model
from tournament.models import Tournament
from CustomUser.models import CustomUser


User = CustomUser

# Création d'un tournoi
tournament = Tournament.objects.create(
    name="Nom du Tournoi",
    max_participants=3,
    is_active=False,
    is_finished=False
)

# Sélection de 8 utilisateurs existants de la base de données
users = User.objects.all()[:3]  # Assurez-vous d'avoir au moins 8 utilisateurs

# Ajout des utilisateurs au tournoi
for user in users:
    tournament.user.add(user)

user = User.objects.get(username="aceek")
tournament.ownerUser = user
tournament.save()

print("Tournoi créé et utilisateurs ajoutés avec succès.")
