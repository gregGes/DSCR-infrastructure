#!/bin/bash
if [ ! -d /tmp/images ]; then
	mkdir -p /tmp/images
fi
cd /tmp/images
{{range service "containers" }} 
echo {{.ID}}
IMAGE=`docker images {{.ID}} | grep {{.ID}}`
if [ -z "$IMAGE" ]; then
	scp -oStrictHostKeyChecking=no -P 2222 {{.Address}}:~/{{ index .Tags 0 }} .
	tar -xvf {{.ID}}.tar >/dev/null
	rm {{.ID}}.tar
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

