#!/bin/sh

export VAULT_TOKEN=$(grep 'token ' /home/user/api/token.cfg | awk '{print $2}')

export DB_CONF=$(curl --cacert /vault-cert/vault.crt -X 'GET' 'https://vault:8200/v1/secret/db_conf' -H 'accept */*' -H "X-Vault-Token: $VAULT_TOKEN" | jq -r .data)

export API_CONF=$(curl --cacert /vault-cert/vault.crt -X 'GET' 'https://vault:8200/v1/secret/api_conf' -H 'accept */*' -H "X-Vault-Token: $VAULT_TOKEN" | jq -r .data)

export EMAIL_CONF=$(curl --cacert /vault-cert/vault.crt -X 'GET' 'https://vault:8200/v1/secret/email_conf' -H 'accept */*' -H "X-Vault-Token: $VAULT_TOKEN" | jq -r .data)

export POSTGRES_DB=$(echo $DB_CONF | jq -r .name)

export POSTGRES_USER=$(echo $DB_CONF | jq -r .username)

export POSTGRES_PASSWORD=$(echo $DB_CONF | jq -r .password)

export POSTGRES_HOST=$(echo $DB_CONF | jq -r .host)

export POSTGRES_PORT=$(echo $DB_CONF | jq -r .port)

export DEBUG_VAR=$(echo $API_CONF | jq -r .debug)

export HOST=$(echo $API_CONF | jq -r .host_machine)

export PORT=$(echo $API_CONF | jq -r .port_machine)

export DJANGO_SECRET=$(echo $API_CONF | jq -r .secret)

export DOMAIN=$(echo $API_CONF | jq -r .domain)

export OAUTH_UID=$(echo $API_CONF | jq -r .oauth_uid)

export OAUTH_SECRET=$(echo $API_CONF | jq -r .oauth_secret)

export OAUTH_REDIRECT_URI=$(echo $API_CONF | jq -r .domain)

export EMAIL_HOST=$(echo $EMAIL_CONF | jq -r .host)

export EMAIL_PORT=$(echo $EMAIL_CONF | jq -r .port)

export EMAIL_USE_TLS=$(echo $EMAIL_CONF | jq -r .use_tls)

export EMAIL_HOST_USER=$(echo $EMAIL_CONF | jq -r .user)

export EMAIL_HOST_PASSWORD=$(echo $EMAIL_CONF | jq -r .password)

exec python3 /app/start_server.py



