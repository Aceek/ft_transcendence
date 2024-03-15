ARG STACK_VERSION

FROM docker.elastic.co/elasticsearch/elasticsearch:${STACK_VERSION}

USER root

RUN apt-get update && apt-get -y install curl jq

USER elasticsearch
