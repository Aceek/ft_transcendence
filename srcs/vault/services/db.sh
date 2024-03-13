#!/bin/sh

apt update && apt install -y curl jq;

export VAULT_TOKEN=$(grep 'token ' /root/db/token.cfg | awk '{print $2}')

export DB_CONF=$(curl --cacert /vault-cert/vault.crt -X 'GET' 'https://vault:8200/v1/secret/db_conf' -H 'accept */*' -H "X-Vault-Token: $VAULT_TOKEN" | jq -r .data)

export POSTGRES_DB=$(echo $DB_CONF | jq -r .name)

export POSTGRES_USER=$(echo $DB_CONF | jq -r .username)

export POSTGRES_PASSWORD=$(echo $DB_CONF | jq -r .password)

export POSTGRES_HOST=$(echo $DB_CONF | jq -r .host)

export POSTGRES_PORT=$(echo $DB_CONF | jq -r .port)

unset DB_CONF DB_SUPER VAULT_TOKEN

exec docker-entrypoint.sh postgres
