#!/bin/bash

export CT_URL="http://bit.ly/15uhv24"

curl -L $CT_URL | tar -C /usr/local/bin --strip-components 1 -zxf -

mkdir /etc/consul-templates

export CT_FILE="/etc/consul-templates/nginx.conf"

export NX_FILE="/etc/nginx/conf.d/app.conf"
export MID_FILE="/tmp/appdata"

export CONSUL=`ip route | grep default | awk -F' ' '{ print $3 }'`
export SERVICE="consul-8500"

/usr/sbin/nginx -c /etc/nginx/nginx.conf \
    & CONSUL_TEMPLATE_LOG=debug consul-template \
      -consul=$CONSUL:8500 \
        -template "$CT_FILE:$MID_FILE:/usr/bin/process.sh";exit 0
/usr/sbin/nginx -c /etc/nginx/nginx.conf \
    & CONSUL_TEMPLATE_LOG=debug consul-template \
      -consul=$CONSUL \
        -template "$CT_FILE:$MID_FILE:/usr/bin/process.sh";exit 0


