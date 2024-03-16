#!/bin/bash

export VAULT_TOKEN=$(grep 'token ' /secret/token.cfg | awk '{print $2}')

export KIBANA=$(curl --cacert /vault-cert/vault.crt -X 'GET' 'https://vault:8200/v1/secret/kibana' -H 'accept */*' -H "X-Vault-Token: $VAULT_TOKEN" | jq -r .data)

export SERVERNAME=$(echo $KIBANA | jq -r .servername)

export ELASTICSEARCH_HOSTS=$(echo $KIBANA | jq -r .elastic_search_hosts)

export ELASTICSEARCH_USERNAME=$(echo $KIBANA | jq -r .elastic_search_username)

export ELASTICSEARCH_PASSWORD=$(curl --cacert /vault-cert/vault.crt -X 'GET' 'https://vault:8200/v1/secret/kibana_passwd' -H 'accept */*' -H "X-Vault-Token: $VAULT_TOKEN" | jq -r .data.password)

export ELASTICSEARCH_SSL_CERTIFICATEAUTHORITIES=$(echo $KIBANA | jq -r .elastic_search_ssl_certificate_auth)

export XPACK_SECURITY_ENCRYPTIONKEY=$(echo $KIBANA | jq -r .encryption_key)

export XPACK_ENCRYPTEDSAVEDOBJECTS_ENCRYPTIONKEY=$(echo $KIBANA | jq -r .encryption_key)

export XPACK_REPORTING_ENCRYPTIONKEY=$(echo $KIBANA | jq -r .encryption_key)

export SERVER_SSL_ENABLED=$(echo $KIBANA | jq -r .server_ssl_enabled)

export SERVER_SSL_KEY=$(echo $KIBANA | jq -r .server_ssl_key)

export SERVER_SSL_CERTIFICATE=$(echo $KIBANA | jq -r .server_ssl_certificate)

exec /bin/tini -- /usr/local/bin/kibana-docker

# exec /usr/local/bin/kibana-docker