FROM nginx:latest

RUN apt-get update -qq && apt-get -y install curl

COPY  execute.sh /usr/bin/execute.sh

COPY nginx.conf /etc/consul-templates/nginx.conf
COPY process.sh /usr/bin/process.sh

CMD ["/usr/bin/execute.sh"]
