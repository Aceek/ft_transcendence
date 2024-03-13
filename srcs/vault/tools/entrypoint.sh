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

# Unset the VAULT_UNSEAL_KEY variable
unset VAULT_UNSEAL_KEY

# Get the root token
export VAULT_TOKEN=$(cat /vault/secrets/vault_token.cfg)

# Generate the tokens for each services
vault token create -policy=db-policy -period=1h -orphan > /vault/secrets/db/token.cfg
vault token create -policy=api-policy -period=1h -orphan > /vault/secrets/api/token.cfg

# Unset the root token
unset VAULT_TOKEN

# Wait for the server
wait $VAULT_PID
