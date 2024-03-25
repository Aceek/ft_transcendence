#!/bin/bash

sleep 10

export VAULT_TOKEN=$(grep 'token ' /secret/token.cfg | awk '{print $2}')

export METRICBEAT=$(curl --cacert /vault-cert/vault.crt -X 'GET' 'https://vault:8200/v1/secret/metricbeat01' -H 'accept */*' -H "X-Vault-Token: $VAULT_TOKEN" | jq -r .data)

export ELASTIC_USER=$(echo $METRICBEAT | jq -r .elastic_user)

export ELASTIC_PASSWORD=$(curl --cacert /vault-cert/vault.crt -X 'GET' 'https://vault:8200/v1/secret/elastic_passwd' -H 'accept */*' -H "X-Vault-Token: $VAULT_TOKEN" | jq -r .data.password)

export ELASTIC_HOSTS=$(echo $METRICBEAT | jq -r .elastic_hosts)

export KIBANA_HOSTS=$(echo $METRICBEAT | jq -r .kibana_hosts)

export LOGSTASH_HOSTS=$(echo $METRICBEAT | jq -r .logstash_hosts)

exec /usr/local/bin/docker-entrypoint -environment container
