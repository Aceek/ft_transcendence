#!/usr/bin/env python3
# script python create users a lancer dans le terminal shell python 

import os
import django
import random
import string

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from CustomUser.models import CustomUser

def generate_random_username(length=8):
    """Génère un nom d'utilisateur aléatoire."""
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(length))

def create_test_users(n, password):
    """Crée N utilisateurs de test."""
    for _ in range(n):
        username = generate_random_username()
        email = f"{username}@example.com"
        user = CustomUser.objects.create_user(username=username, email=email, password=password)
        user.is_active = True
        user.save()
        print(f"Utilisateur {username} créé avec succès.")

# Nombre d'utilisateurs à créer
NUMBER_OF_USERS = 10
# Mot de passe commun pour tous les utilisateurs
COMMON_PASSWORD = 'password'

create_test_users(NUMBER_OF_USERS, COMMON_PASSWORD)
