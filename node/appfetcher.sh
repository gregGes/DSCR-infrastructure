#!/bin/bash
echo `date` >> /home/ubuntu/date.txt
if [ ! -d /tmp/images ]; then
	mkdir -p /tmp/images
fi
cd /tmp/images
{{range service "containers" }} 
echo {{.ID}}
IMAGE=`docker images {{.ID}} | grep {{.ID}}`
if [ -z "$IMAGE" ]; then
	curl http://{{.Address}}:{{.Port}}/{{ index .Tags 0 }} | tar -xf - 2>/dev/null
else
	echo "image already exist"
fi

{{end}}

for f in *
do
	cd $f
	echo `pwd`
	echo "docker build -t $f ." 
	docker build -t $f . 
	echo "finsihed"
	cd ..
	rm -rf $f 
done

