FROM node:latest

WORKDIR /app

COPY app/ .

RUN npm install

RUN useradd -ms /bin/bash user

USER user