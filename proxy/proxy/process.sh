#!/bin/sh

MIDFILE=/tmp/appdata
ASORTED=/tmp/asorted
NGINX_FILE=/etc/nginx/conf.d/app.conf
CF_FILE=/tmp/cftmp

rm -f $ASORTED
rm -f $CF_FILE
touch $CF_FILE
cat $MIDFILE | sed '/^ $/d' | sed '/^$/d' | sort > $ASORTED

H=""
while read line
do
	HOST=`echo $line | awk -F '=' '{ print $1 }'`
	if [ ! "$HOST" = "$H" ]; then
		echo $HOST
		H=$HOST
		echo ' }' >> $CF_FILE
		echo '}' >> $CF_FILE
		echo 'server {' >>$CF_FILE
		echo ' listen 80;' >>$CF_FILE
		echo " server_name $HOST;" >>$CF_FILE
		echo ' location / {' >>$CF_FILE
	fi
	APU=`echo $line | awk -F '=' '{ print $2 }'`
	echo "  proxy_pass http://$APU/;">>$CF_FILE
done < $ASORTED

echo ' }' >> $CF_FILE
echo '}' >> $CF_FILE

tail -n +3 $CF_FILE>$NGINX_FILE
/usr/sbin/nginx -s reload



