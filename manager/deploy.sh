#!/bin/bash

#####################################################
#### Deployment script to create the DSCR master #### 
#####################################################

set -x 

### initialisation of the variable
sudo hostname master

_user="$(id -u -n)"
SRC=`pwd`
INSTALL_DIR="/opt/manager_DSCR"
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

### add the ssh-key of the container to the authorized_key file ###

sudo cat id_rsa.pub >> /home/${_user}/.ssh/authorized_keys


### creation of the docker_images directory ###

sudo mkdir /home/${_user}/docker_images


### initialisation of the consul ###

sudo wget https://releases.hashicorp.com/consul/0.5.2/consul_0.5.2_linux_amd64.zip

sudo unzip consul_0.5.2_linux_amd64.zip

sudo m consul_0.5.2_linux_amd64.zip


sudo mv consul /usr/bin

sudo mkdir /var/consul

sudo mv consul.conf /etc/init

sudo mkdir -p /etc/consul.d/server

sudo mv config.json /etc/consul.d/server


### installation of docker ###

wget -qO- https://get.docker.com/ | sh

sudo usermod -aG docker $_user

### reinitialise ###

sudo service consul stop
sudo rm -f /var/consul/* > /dev/null 2>&1
sudo service consul start

sleep 2


sudo rm -f /etc/docker/key.json
sudo rm /etc/default/docker
sudo mv docker /etc/default
cat /etc/default/docker | sed s/PLACEHOLDER/manager/ > /tmp/ddef
sudo mv /tmp/ddef /etc/default/docker
sudo service docker restart
sleep 3

sudo mv Cloudbroker.py /home/$_user
sudo mv main.py /home/$_user

sudo chown -R ${_user}:${_user} outputs/pickled
cd ${SRC}

exit 0

