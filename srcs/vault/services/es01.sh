#!/bin/sh

sleep 2

export VAULT_TOKEN=$(grep 'token ' /secret/token.cfg | awk '{print $2}')

export ES_01=$(curl --cacert /vault-cert/vault.crt -X 'GET' 'https://vault:8200/v1/secret/es01' -H 'accept */*' -H "X-Vault-Token: $VAULT_TOKEN" | jq -r .data)

export ELASTIC_PASSWORD=$(curl --cacert /vault-cert/vault.crt -X 'GET' 'https://vault:8200/v1/secret/elastic_passwd' -H 'accept */*' -H "X-Vault-Token: $VAULT_TOKEN" | jq -r .data.password)

env node.name=$(echo $ES_01 | jq -r .node_name) \
    cluster.name=$(echo $ES_01 | jq -r .cluster_name) \
    discovery.type=$(echo $ES_01 | jq -r .discovery_type) \
    ELASTIC_PASSWORD=$(echo $ELASTIC_PASSWORD) \
    bootstrap.memory_lock=$(echo $ES_01 | jq -r .bootstrap_memory_lock) \
    xpack.security.enabled=$(echo $ES_01 | jq -r .xpack_security_enabled) \
    xpack.security.http.ssl.enabled=$(echo $ES_01 | jq -r .xpack_security_http_ssl_enabled) \
    xpack.security.http.ssl.key=$(echo $ES_01 | jq -r .xpack_security_http_ssl_key) \
    xpack.security.http.ssl.certificate=$(echo $ES_01 | jq -r .xpack_security_http_ssl_certificate) \
    xpack.security.http.ssl.certificate_authorities=$(echo $ES_01 | jq -r .xpack_security_http_ssl_certificate_authorities) \
    xpack.security.transport.ssl.enabled=$(echo $ES_01 | jq -r .xpack_security_transport_ssl_enabled) \
    xpack.security.transport.ssl.key=$(echo $ES_01 | jq -r .xpack_security_transport_ssl_key) \
    xpack.security.transport.ssl.certificate=$(echo $ES_01 | jq -r .xpack_security_transport_ssl_certificate) \
    xpack.security.transport.ssl.certificate_authorities=$(echo $ES_01 | jq -r .xpack_security_transport_ssl_certificate_authorities) \
    xpack.security.transport.ssl.verification_mode=$(echo $ES_01 | jq -r .xpack_security_transport_ssl_verification_mode) \
    xpack.license.self_generated.type=$(echo $ES_01 | jq -r .xpack_license_self_generated_type) \
    /usr/local/bin/docker-entrypoint.sh

