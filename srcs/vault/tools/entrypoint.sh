#!/bin/sh

sh /vault/tools/wait-certs.sh

set -e

if [ ! -f "/vault/secrets/initialized" ]; then
    echo "Vault is not initialized."
    exit 1
fi

# Start the server in background
vault server -config=/vault/config/vault.json &

# Store the PID of the server
VAULT_PID=$!

#Wait for the server to start
sleep 10

# Get the unseal key
VAULT_UNSEAL_KEY=$(cat /vault/secrets/vault_unseal_key.cfg)

# Unseal the vault
vault operator unseal $VAULT_UNSEAL_KEY

sleep 2

# Unset the VAULT_UNSEAL_KEY variable
unset VAULT_UNSEAL_KEY

# Get the root token
export VAULT_TOKEN=$(cat /vault/secrets/vault_token.cfg)

# Generate the tokens for each services
vault token create -policy=db-policy -period=4h -orphan > /vault/secrets/db/token.cfg
vault token create -policy=api-policy -period=4h -orphan > /vault/secrets/api/token.cfg
vault token create -policy=elk-setup-policy -period=4h -orphan > /vault/secrets/elk-setup/token.cfg
vault token create -policy=elk-es01-policy -period=4h -orphan > /vault/secrets/elk-es01/token.cfg
vault token create -policy=elk-kibana-policy -period=4h -orphan > /vault/secrets/elk-kibana/token.cfg
vault token create -policy=elk-metricbeat01-policy -period=4h -orphan > /vault/secrets/elk-metricbeat01/token.cfg
vault token create -policy=elk-logstash01-policy -period=4h -orphan > /vault/secrets/elk-logstash01/token.cfg
vault token create -policy=elk-filebeat01-policy -period=4h -orphan > /vault/secrets/elk-filebeat01/token.cfg

# Unset the root token
unset VAULT_TOKEN

# Wait for the server
wait $VAULT_PID
