FROM nginx:alpine

RUN apk update

RUN apk add --no-cache \
    git \
    g++ \
    make \
    libtool \
    pcre-dev \
    linux-headers \
    curl-dev \
    yajl-dev \
    geoip-dev \
    libxml2-dev \
    autoconf \
    automake \
    libtool \
    m4

COPY nginx.conf /etc/nginx/nginx.conf

RUN git clone https://github.com/owasp-modsecurity/ModSecurity.git /opt/ModSecurity

RUN git clone https://github.com/owasp-modsecurity/ModSecurity-nginx.git /opt/ModSecurity-nginx

RUN git clone https://github.com/coreruleset/coreruleset.git /opt/modsecurity-crs

WORKDIR /opt/ModSecurity

RUN git submodule init

RUN git submodule update

RUN ./build.sh

RUN ./configure

RUN make

RUN make install

WORKDIR /opt/

RUN export NGINX_VERSION=$(nginx -v 2>&1 | cut -d'/' -f2)

RUN wget http://nginx.org/download/nginx-$NGINX_VERSION.tar.gz

RUN tar -xvzf nginx-$NGINX_VERSION.tar.gz

WORKDIR /opt/nginx-$NGINX_VERSION

RUN ./configure --add-dynamic-module=/opt/ModSecurity-nginx --with-compat

RUN make modules

RUN mkdir -p /etc/nginx/modules

RUN cp objs/ngx_http_modsecurity_module.so /etc/nginx/modules/

WORKDIR /opt/modsecurity-crs

RUN mv crs-setup.conf.example crs-setup.conf

RUN mv rules/REQUEST-900-EXCLUSION-RULES-BEFORE-CRS.conf.example rules/REQUEST-900-EXCLUSION-RULES-BEFORE-CRS.conf

WORKDIR /opt

RUN mv modsecurity-crs /usr/local/

RUN mkdir -p /etc/nginx/modsec

RUN cp /opt/ModSecurity/unicode.mapping /etc/nginx/modsec/

COPY modsec-conf/modsecurity.conf /etc/nginx/modsec/modsecurity.conf

COPY modsec-conf/main.conf /etc/nginx/modsec/main.conf

# CMD ["tail", "-f", "/dev/null"]
