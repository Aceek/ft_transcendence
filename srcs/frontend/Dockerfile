FROM node:latest

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

EXPOSE 3000

RUN useradd -ms /bin/bash user

# Définissez cet utilisateur comme l'utilisateur par défaut
USER user