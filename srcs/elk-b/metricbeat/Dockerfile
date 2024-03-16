ARG METRICBEAT_VERSION


FROM docker.elastic.co/beats/metricbeat:${METRICBEAT_VERSION}

#COPY metricbeat.yml and chmod 400
COPY --chown=root:metricbeat ./metricbeat.yml /usr/share/metricbeat/metricbeat.yml

USER root

RUN apt-get update && apt-get install -y curl jq

RUN chmod go-w /usr/share/metricbeat/metricbeat.yml
# USER metricbeat
