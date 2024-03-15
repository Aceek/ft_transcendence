path "secret/elastic_passwd" {
  capabilities = ["read"]
}

path "secret/kibana_passwd" {
  capabilities = ["read"]
}

path "secret/logstash_internal" {
  capabilities = ["read"]
}
