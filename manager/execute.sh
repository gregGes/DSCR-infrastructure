############################################################
##        Script to be executed when job launched         ##
############################################################
set -x 


# Parameters

SRC_DIR=`pwd`
INSTALL_DIR="/opt/manager_DSCR"
JOB_PACKAGE=input.tar.gz
DATE=`date "+%d%m%y%H%M%S"`
HOST_NAME=master
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


if [ $# -eq 0 ]; then 
        echo "0 arugments supplied"
        exit 1
elif [ $# -gt 0 ]; then 
        case $1 in
        -start) sleep 3
                ${INSTALL_DIR}/init.sh ${NUM} ${HOST_IP} ${HOST_NAME};;
        *) echo "invalid argument";;
    esac
fi

exit 0





