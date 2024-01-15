FROM python:3.10

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY . /app/

RUN apt-get update && apt-get install -y zsh

RUN pip install -r requirements.txt

# Créez un utilisateur avec le nom spécifié
RUN useradd -ms /bin/bash user

# Définissez cet utilisateur comme l'utilisateur par défaut
USER user