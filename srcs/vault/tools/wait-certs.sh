#!/bin/sh

while [ ! -f /vault-cert/vault.crt ]; do
    echo "Waiting for certs-generator to generate the certificates...";
    sleep 5;
done;
echo "Certificates found, starting Vault...";
