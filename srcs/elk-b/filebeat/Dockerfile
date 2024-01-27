ARG FILEBEAT_VERSION

FROM docker.elastic.co/beats/filebeat:${FILEBEAT_VERSION}


#Copy filebeaty.yml to the container and cmd 400
COPY --chown=root:filebeat ./filebeat.yml /usr/share/filebeat/filebeat.yml

USER root
RUN chmod go-w /usr/share/filebeat/filebeat.yml
# USER filebeat
