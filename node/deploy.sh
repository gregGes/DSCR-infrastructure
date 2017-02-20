#!/bin/bash

###############################################################
#### Deployment script to create the DSCR application node #### 
###############################################################

set -x 


### initialisation of the variable

_user="$(id -u -n)"
SRC=`pwd`
INSTALL_DIR="/opt/node_DSCR"
INSTALL_PACKAGE="install.tar.gz"


### moving to correct directory 
sudo mkdir -p ${INSTALL_DIR}

sudo cp ${INSTALL_PACKAGE} ${INSTALL_DIR}

cd ${INSTALL_DIR}
sudo tar -zxvf ${INSTALL_PACKAGE}

##creation of group and ssh

cat /etc/group | sed s/$_user$/ubuntu,xyzzy/ > /tmp/group

sudo cp /tmp/group /etc/group

sudo adduser --disabled-password --quiet --gecos "foo" xyzzy


sudo mkdir ~xyzzy/kit
sudo chmod 777 ~xyzzy/kit
sudo mv ssh ~xyzzy/kit/
cd ~xyzzy/kit
sudo rm -rf ../.ssh
sudo mv ssh ../.ssh

#change port to ssh to 2222 for CloudSigma
cat /etc/ssh/sshd_config > /tmp/sshd_config
echo "Port 2222" >> /tmp/sshd_config
sudo cp /tmp/sshd_config /etc/ssh/sshd_config
sudo service ssh restart
sudo netstat -alnp | grep "22"

sudo chown -R xyzzy:xyzzy ~xyzzy

echo "xyzzy ALL=(ALL) NOPASSWD:ALL" > /tmp/sd
sudo mv /tmp/sd /etc/sudoers.d/91-xyzzy
sudo chown 0:0 /etc/sudoers.d/91-xyzzy

cd ${INSTALL_DIR}

### initialisation of the consul ###
sudo wget https://releases.hashicorp.com/consul/0.7.3/consul_0.7.3_linux_amd64.zip

sudo unzip consul_0.7.3_linux_amd64.zip

rm consul_0.7.3_linux_amd64.zip

sudo mv consul /usr/bin

sudo mkdir /var/consul

sudo mv consul.conf /etc/init

sudo mkdir -p /etc/consul.d/server

sudo mv config.json /etc/consul.d/server



### mv registrator to /usr/bin ###

#sudo mv registrator /usr/bin 


### installation of docker ###

wget -qO- https://get.docker.com/ | sh

sudo usermod -aG docker $_user

### reinitialise 

sudo rm -f /etc/docker/key.json > /dev/null 2>&1
sudo rm /etc/default/docker
sudo mv docker /etc/default
sudo mkdir -p /home/$_user/.docker
sudo mv ${INSTALL_DIR}/docker-config.json /home/$_user/.docker/config.json
sudo service docker restart

### creation of the swap memory
sudo rm -f /swapfile
sudo dd if=/dev/zero of=/swapfile bs=1M count=1024  
sudo chown root /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

### back to the source directory
cd ${SRC}

exit 0

