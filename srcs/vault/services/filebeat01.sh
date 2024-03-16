#!/bin/bash

export VAULT_TOKEN=$(grep 'token ' /secret/token.cfg | awk '{print $2}')

export LOGSTASH_HOSTS=$(curl --cacert /vault-cert/vault.crt -X 'GET' 'https://vault:8200/v1/secret/filebeat01' -H 'accept */*' -H "X-Vault-Token: $VAULT_TOKEN" | jq -r .data.logstash_hosts)

exec /usr/local/bin/docker-entrypoint -environment container