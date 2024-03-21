#!/bin/sh

sh /vault/tools/wait-certs.sh

set -e

export MACHINE_ADDR="localhost"

export MACHINE_PORT=9443

# Start the server in background
vault server -config=/vault/config/vault.json &

# Store the PID of the server
VAULT_PID=$!

#Wait for the server to start
sleep 10

# Init the operator with one unseal key and one root key
VAULT_INIT=$(vault operator init -t 1 -n 1)

# Get the unseal key
VAULT_UNSEAL_KEY=$(echo $VAULT_INIT | awk '{print $4}')

# Get the root token
export VAULT_TOKEN=$(echo $VAULT_INIT | awk '{print $8}')

# Unset the VAULT_INIT variable
unset VAULT_INIT

# Make dir for the secrets
mkdir -p /vault/secrets

# Store the unseal key in a file
echo $VAULT_UNSEAL_KEY > /vault/secrets/vault_unseal_key.cfg

# Store the root token in a file
echo $VAULT_TOKEN > /vault/secrets/vault_token.cfg

# Unseal the vault
vault operator unseal $VAULT_UNSEAL_KEY

# Unset the VAULT_UNSEAL_KEY variable
unset VAULT_UNSEAL_KEY

# Enable the kv secret engine
vault secrets enable -path=secret kv

# Set the different secret in the vault
vault kv put secret/db_conf username="VyWW8oJdLI" password="bPO7hydkxXsGf48HEZ6HoQ==" name="transcendence_db" host="db" port=5432

vault kv put secret/api_conf \
    secret="7f!#tzcqmth6r82xs1u6hf61rhg&#146-==_8lq#xdv^)0e@f" \
    debug="True" \
    oauth_uid="u-s4t2ud-3daabd13927189f03aa95d1614c0acea56e9d2784d1b30040e117b065410f3e1" \
    oauth_secret="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" \
    domain="https://$MACHINE_ADDR:$MACHINE_PORT/" \
    host_machine=$MACHINE_ADDR \
    port_machine=$MACHINE_PORT

vault kv put secret/email_conf \
    host="smtp.gmail.com" \
    port=587 \
    use_tls=True \
    user="ft.transcendence.42.fr@gmail.com" \
    password="trwhkbrpebmxnepw"

vault kv put secret/elastic_passwd password="c2FsdXRjZXN0bW9pbGVtb3RkZXBhc3NlCg=="

vault kv put secret/kibana_passwd password="amFpbWVsYXZpZQo="

vault kv put secret/logstash_internal password="TE9HU1RBU0hfSU5URVJOQUxfUEFTU1dPUkQK"

vault kv put secret/es01 node_name=es01 \
    cluster_name=docker-cluster \
    discovery_type=single-node \
    bootstrap_memory_lock=true \
    xpack_security_enabled=true \
    xpack_security_http_ssl_enabled=true \
    xpack_security_http_ssl_key=certs/es01/es01.key \
    xpack_security_http_ssl_certificate=certs/es01/es01.crt \
    xpack_security_http_ssl_certificate_authorities=certs/ca/ca.crt \
    xpack_security_transport_ssl_enabled=true \
    xpack_security_transport_ssl_key=certs/es01/es01.key \
    xpack_security_transport_ssl_certificate=certs/es01/es01.crt \
    xpack_security_transport_ssl_certificate_authorities=certs/ca/ca.crt \
    xpack_security_transport_ssl_verification_mode=certificate \
    xpack_license_self_generated_type=basic

vault kv put secret/kibana servername="kibana"\
    elastic_search_hosts="https://es01:9200" \
    elastic_search_username="kibana_system" \
    elastic_search_ssl_certificate_auth="config/certs/ca/ca.crt" \
    encryption_key="c34d38b3a14956121ff2170e5030b471551370178f43e5626eec58b04a30fae2" \
    server_ssl_enabled=true \
    server_ssl_key=config/certs/kibana/kibana.key \
    server_ssl_certificate=config/certs/kibana/kibana.crt

vault kv put secret/metricbeat01 elastic_user=elastic \
    elastic_hosts=https://es01:9200 \
    kibana_hosts=https://kibana:5601 \
    logstash_hosts=http://logstash01:9600

vault kv put secret/logstash01 xpack_monitoring_enabled=false \
    elastic_user=elastic \
    elastic_hosts=https://es01:9200

vault kv put secret/filebeat01 logstash_hosts="logstash01:5044"

# Load policies
vault policy write db-policy /vault/policies/db-policy.hcl
vault policy write api-policy /vault/policies/api-policy.hcl
vault policy write elk-setup-policy /vault/policies/elk-setup.hcl
vault policy write elk-es01-policy /vault/policies/elk-es01.hcl
vault policy write elk-kibana-policy /vault/policies/elk-kibana.hcl
vault policy write elk-metricbeat01-policy /vault/policies/elk-metricbeat.hcl 
vault policy write elk-logstash01-policy /vault/policies/elk-logstash01.hcl
vault policy write elk-filebeat01-policy /vault/policies/elk-filebeat01.hcl

# Unset the VAULT_TOKEN
unset VAULT_TOKEN

# Create a file to indicate that the vault is initialized
touch /vault/secrets/initialized

# Kill the vault server
kill $VAULT_PID