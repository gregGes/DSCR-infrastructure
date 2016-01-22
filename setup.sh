#!/bin/bash
set -x
SRC=`pwd`

## add public-key to authorized_keys of the manager instance
if [ ! -f ~/.ssh/id_rsa.pub ]; then
        echo "public key doesn't exist create a pair first and rerun the setup script"
        exit 1
fi
mkdir -p ${SRC}/manager/ssh

## generate ssh key-pair
ssh-keygen -f ${SRC}/manager/ssh/id_rsa -t rsa -N ''

cat ~/.ssh/id_rsa.pub > ${SRC}/manager/ssh/authorized_keys

## add the generated key pair inside authorized_keys of the node and proxy
mkdir -p ${SRC}/node/ssh
mkdir -p ${SRC}/proxy/ssh

cat ${SRC}/manager/ssh/id_rsa.pub > ${SRC}/node/ssh/authorized_keys
cat ${SRC}/manager/ssh/id_rsa.pub > ${SRC}/proxy/ssh/authorized_keys

read -p "give the Atlas token:"  ATLAS_TOKEN
read -p "give the Atlas infrastructure name:" ATLAS_NAME
read -p "give the Consul key:" CONSUL_KEY

cat ${SRC}/manager/config.json | sed s/ATLAS_TOKEN/${ATLAS_TOKEN}/ > /tmp/dscr
mv /tmp/dscr ${SRC}/manager/config.json
cat ${SRC}/manager/config.json | sed s/ATLAS_NAME/${ATLAS_NAME}/ > /tmp/dscr
mv /tmp/dscr ${SRC}/manager/config.json
cat ${SRC}/manager/config.json | sed s/CONSUL_KEY/${CONSUL_KEY}/ > /tmp/dscr
mv /tmp/dscr ${SRC}/manager/config.json

cp ${SRC}/manager/config.json ${SRC}/node/config.json
cp ${SRC}/manager/config.json ${SRC}/proxy/config.json

echo "setup done"
exit 0
