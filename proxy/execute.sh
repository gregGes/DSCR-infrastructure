############################################################
##        Script to be executed when job launched         ##
############################################################

# parameters
 
SRC=`pwd`
ROLE=$1
RAND_NUM=`cat /dev/urandom | tr -cd 'a-f0-9' | head -c 20`
NODE_NAME=${ROLE}_${RAND_NUM}
INSTALL_DIR=/opt/proxy_DSCR
# Reseed consul

sudo service consul stop

sudo rm -f /var/consul/* > /dev/null 2>&1

sudo service consul start

sleep 2

NUM=0
while :
do
    RES=`sudo ifconfig eth${NUM}| grep 'inet addr' | cut -d ':' -f 2 | awk '{ print $1 }' `
    #(echo $RES | grep -E '^(192\.168|10\.|172\.1[6789]\.|172\.2[0-9]\.|172\.3[01]\.)' ) && break || echo "did not match"
    if [[ $RES =~ ^([0-9]{1,3})[.]([0-9]{1,3})[.]([0-9]{1,3})[.]([0-9]{1,3})$ ]]; then
        for (( i=1; i<${#BASH_REMATCH[@]}; ++i ))
        do
            (( ${BASH_REMATCH[$i]} <= 255 )) || { echo "bad ip" >&2; }

        done
        echo "correct ip $RES" >&2
        break;
    else
        echo "bad ip" >&2

    fi

    NUM=$(($NUM + 1 ))
done


HOST_IP=${RES}
sudo service consul stop
sudo rm -f /tmp/cdef > /dev/null 2>&1
cat /etc/init/consul.conf | sed s/INTERFACE/eth${NUM}/ > /tmp/cdef
sudo mv /tmp/cdef /etc/init/consul.conf
cat /etc/consul.d/server/config.json | sed s/IP_ADDRESS/${HOST_IP}/ > /tmp/cdef
sudo mv /tmp/cdef /etc/consul.d/server/config.json
cat /etc/consul.d/server/config.json | sed s/NODE_NAME/${NODE_NAME}/ > /tmp/cdef
sudo mv /tmp/cdef /etc/consul.d/server/config.json

sudo service consul start
sleep 3


# Reseed docker and give it a role

sudo service docker stop

sudo rm -f /etc/docker/key.json > /dev/null 2>&1
sudo rm -f /tmp/ddef > /dev/null 2>&1

cat /etc/default/docker | sed s/PLACEHOLDER/proxy/ > /tmp/ddef
sudo mv /tmp/ddef /etc/default/docker
sudo service docker start
sleep 3

# start swarm

sudo mv ${SRC}/swarm.token ${INSTALL_DIR}
TOKEN=`cat ${INSTALL_DIR}/swarm.token`

docker run -d swarm join --addr=${HOST_IP}:2375 token://${TOKEN}

docker run -d --net=host --volume=/var/run/docker.sock:/tmp/docker.sock gliderlabs/registrator:latest consul://localhost:8500/swarm


sleep infinity

exit 0
