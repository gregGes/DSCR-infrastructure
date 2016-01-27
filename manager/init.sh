#################################################################
##        init Script to be executed when job launched         ##
#################################################################
set -x 
NUM=$1
HOST_IP=$2
HOST_NAME=$3
INSTALL_DIR=/opt/manager_DSCR


sudo service consul stop

sudo rm -f /tmp/cdef > /dev/null 2>&1
cat /etc/init/consul.conf | sed s/INTERFACE/eth${NUM}/ > /tmp/cdef
sudo mv /tmp/cdef /etc/init/consul.conf
cat /etc/consul.d/server/config.json | sed s/IP_ADDRESS/${HOST_IP}/ > /tmp/cdef
sudo mv /tmp/cdef /etc/consul.d/server/config.json
cat /etc/consul.d/server/config.json | sed s/NODE_NAME/${HOST_NAME}/ > /tmp/cdef
sudo mv /tmp/cdef /etc/consul.d/server/config.json

sudo service consul start
sleep 3

# create a token for the swarm
docker pull swarm
docker run --rm swarm create > swarm.token

TOKEN=`cat swarm.token`

sudo mv swarm.token ${INSTALL_DIR}


docker run -d -p 22375:2375 -t swarm manage token://${TOKEN}


exit 0
