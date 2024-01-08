FROM python:3.10

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY . /app/

RUN pip install -r requirements.txt

# Créez un utilisateur non privilégié
RUN useradd -ms /bin/bash myuser

# Définissez cet utilisateur comme l'utilisateur par défaut
USER myuser
