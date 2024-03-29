#!/bin/bash

apt-get update && apt-get install -y curl jq

export VAULT_TOKEN=$(grep 'token ' /secret/token.cfg | awk '{print $2}')

export ELASTIC_PASSWORD=$(curl --cacert /vault-cert/vault.crt -X 'GET' 'https://vault:8200/v1/secret/elastic_passwd' -H 'accept */*' -H "X-Vault-Token: $VAULT_TOKEN" | jq -r .data.password)

export KIBANA_PASSWORD=$(curl --cacert /vault-cert/vault.crt -X 'GET' 'https://vault:8200/v1/secret/kibana_passwd' -H 'accept */*' -H "X-Vault-Token: $VAULT_TOKEN" | jq -r .data.password)

export LOGSTASH_INTERNAL_PASSWORD=$(curl --cacert /vault-cert/vault.crt -X 'GET' 'https://vault:8200/v1/secret/logstash_internal' -H 'accept */*' -H "X-Vault-Token: $VAULT_TOKEN" | jq -r .data.password)

if [ x${ELASTIC_PASSWORD} == x ]; then
          echo "Set the ELASTIC_PASSWORD environment variable in the .env file";
          exit 1;
        elif [ x${KIBANA_PASSWORD} == x ]; then
          echo "Set the KIBANA_PASSWORD environment variable in the .env file";
          exit 1;
        elif [ x${LOGSTASH_INTERNAL_PASSWORD} == x ]; then
          echo "Set the LOGSTASH_INTERNAL_PASSWORD environment variable in the .env file";
          exit 1;
        fi;
        if [ ! -f config/certs/ca.zip ]; then
          echo "Creating CA";
          bin/elasticsearch-certutil ca --silent --pem -out config/certs/ca.zip;
          unzip config/certs/ca.zip -d config/certs;
        fi;
        if [ ! -f config/certs/certs.zip ]; then
          echo "Creating certs";
          echo -ne \
          "instances:\n"\
          "  - name: es01\n"\
          "    dns:\n"\
          "      - es01\n"\
          "      - localhost\n"\
          "  - name: kibana\n"\
          "    dns:\n"\
          "      - kibana\n"\
          "      - localhost\n"\
          "  - name: logstash\n"\
          "    dns:\n"\
          "      - logstash01\n"\
          "      - localhost\n"\
          "  - name: filebeat\n"\
          "    dns:\n"\
          "      - filebeat01\n"\
          "      - localhost\n"\
          > config/certs/instances.yml;
          bin/elasticsearch-certutil cert --silent --pem -out config/certs/certs.zip --in config/certs/instances.yml --ca-cert config/certs/ca/ca.crt --ca-key config/certs/ca/ca.key;
          unzip config/certs/certs.zip -d config/certs;
        fi;
        echo "Setting file permissions"
        chown -R root:root config/certs;
        find . -type d -exec chmod 750 \{\} \;;
        find . -type f -exec chmod 640 \{\} \;;
        echo "Waiting for Elasticsearch availability";
        until curl -s --cacert config/certs/ca/ca.crt https://es01:9200 | grep -q "missing authentication credentials"; do sleep 30; done;
        echo "Setting kibana_system password";
        until curl -s -X POST --cacert config/certs/ca/ca.crt -u "elastic:${ELASTIC_PASSWORD}" -H "Content-Type: application/json" https://es01:9200/_security/user/kibana_system/_password -d "{\"password\":\"${KIBANA_PASSWORD}\"}" | grep -q "^{}"; do sleep 10; done;
        echo "Setting logstash_system password";
        until curl -s -X POST --cacert config/certs/ca/ca.crt -u "elastic:${ELASTIC_PASSWORD}" -H "Content-Type: application/json" https://es01:9200/_security/user/logstash_system/_password -d "{\"password\":\"${LOGSTASH_INTERNAL_PASSWORD}\"}" | grep -q "^{}"; do sleep 10; done;

        # Add ilm policy to elasticsearch
        echo "Adding ILM policy";
        curl -X PUT --cacert config/certs/ca/ca.crt -u elastic:${ELASTIC_PASSWORD} "https://es01:9200/_ilm/policy/logs_policy" -H 'Content-Type: application/json' -d '{
        "policy": {
            "phases": {
            "hot": {
                "min_age": "0ms",
                "actions": {
                "rollover": {
                    "max_size": "50gb",
                    "max_age": "30d"
                }
                }
            },
            "delete": {
                "min_age": "90d",
                "actions": {
                "delete": {}
                }
            }
            }
        }
        }'

        # Add policy to index
        echo "Adding policy to index template";
        curl -X PUT --cacert config/certs/ca/ca.crt -u elastic:${ELASTIC_PASSWORD} "https://es01:9200/_template/logs_template" -H 'Content-Type: application/json' -d '{
          "index_patterns": ["dev*"],
          "settings": {
            "index.lifecycle.name": "logs_policy",
            "index.lifecycle.rollover_alias": "dev"
          }
        }'
        # try kibana connection
        echo "Waiting for Kibana availability";

        until $(curl --output /dev/null --silent --head --fail --insecure https://kibana:5601); do
            printf 'Waiting for Kibana API...'
            sleep 5
        done
        echo "Kibana is ready. Importing Kibana objects...";
        
        sleep 5
        # import kibana objects
        # curl -k --cacert config/certs/ca/ca.crt \
        # -u elastic:${ELASTIC_PASSWORD} \
        # -X POST "https://kibana:5601/api/saved_objects/_import" \
        # -H 'kbn-xsrf: true' \
        # --form file=@"/saved_objects.ndjson"

        while true; do
          response=$(curl -k --cacert config/certs/ca/ca.crt \
              -u elastic:${ELASTIC_PASSWORD} \
              -X POST "https://kibana:5601/api/saved_objects/_import" \
              -H 'kbn-xsrf: true' \
              --form file=@"/saved_objects.ndjson" \
              -w "%{http_code}" \
              -o /dev/null)

          if [ "$response" -eq 200 ]; then
              echo "La requête a réussi."
              break
          else
              echo "La requête a échoué avec le code de statut HTTP $response. Réessayer..."
              sleep 5
          fi
        done

        echo "All done!";