ARG FILEBEAT_VERSION

FROM docker.elastic.co/beats/filebeat:${FILEBEAT_VERSION}


#Copy filebeaty.yml to the container and cmd 400
COPY --chown=root:filebeat ./filebeat.yml /usr/share/filebeat/filebeat_test.yml


# USER filebeat
