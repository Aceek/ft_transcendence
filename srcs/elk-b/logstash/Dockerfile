ARG STACK_VERSION

FROM docker.elastic.co/logstash/logstash:${STACK_VERSION}

USER root

RUN apt-get update && apt-get install -y curl jq
