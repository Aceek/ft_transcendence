ARG STACK_VERSION

FROM docker.elastic.co/kibana/kibana:${STACK_VERSION}

USER root

RUN apt-get update && apt-get -y install curl jq

USER kibana
