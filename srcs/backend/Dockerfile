FROM python:3.10

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY . /app/

RUN apt-get update && apt-get install -y zsh curl jq

RUN pip install -r requirements.txt


# Créez un utilisateur avec le nom spécifié
RUN useradd -ms /bin/bash user

# create media folder with user permissions
RUN mkdir -p /app/media
RUN chown -R user:user /app/media

# Définissez cet utilisateur comme l'utilisateur par défaut
USER user