
export VAULT_TOKEN=$(grep 'token ' /secret/token.cfg | awk '{print $2}')

export LOGSTASH=$(curl --cacert /vault-cert/vault.crt -X 'GET' 'https://vault:8200/v1/secret/logstash01' -H 'accept */*' -H "X-Vault-Token: $VAULT_TOKEN" | jq -r .data)

export ELASTIC_PASSWORD=$(curl --cacert /vault-cert/vault.crt -X 'GET' 'https://vault:8200/v1/secret/elastic_passwd' -H 'accept */*' -H "X-Vault-Token: $VAULT_TOKEN" | jq -r .data.password)

env xpack.monitoring.enabled=$(echo $LOGSTASH | jq -r .xpack_monitoring_enabled) \
    ELASTIC_USER=$(echo $LOGSTASH | jq -r .elastic_user) \
    ELASTIC_PASSWORD=$(echo $ELASTIC_PASSWORD) \
    ELASTIC_HOSTS=$(echo $LOGSTASH | jq -r .elastic_hosts) \
    /usr/local/bin/docker-entrypoint
