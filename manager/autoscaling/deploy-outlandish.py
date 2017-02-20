#!/usr/bin/python

import urllib, json
from functions import launch_container, container_remove
import argparse 
import time
import socket 
import getpass

url="http://localhost:8500/v1/catalog/nodes"
response=urllib.urlopen(url)
data=json.loads(response.read())
for i in xrange(len(data)):
	if "master" in data[i]['Node']:
		host=json.dumps(data[i]['Address']).strip('"')

user=getpass.getuser().strip('"')

print "deploy tidybooks"
client=raw_input('client name: ')
domain=raw_input('domain name: ')
application=raw_input('directory application: ')
args=dict()
args["location"]=['application']
args["image"]=['mongo']
args["name"]=[client]
args["arguments"]=['/--smallfiles']
print args
launch_container(args)
time.sleep(2)	
url="http://localhost:8500/v1/catalog/service/mongo"
response=urllib.urlopen(url)

data=json.loads(response.read())
for i in xrange(len(data)):
	try:
		if client in data[i]['ServiceTags'][0]:
			address=json.dumps(data[i]['Address']).strip('"')
			port=json.dumps(data[i]['ServicePort']).strip('"')
			print address
			print port
	except TypeError:
		print "service tag null, next"
args=dict()
args["location"]=['application']
args["image"]=['serv-36.felho.sztaki.hu:5000/container-default:1.0']
args["name"]=[client]
args["script"]=['/usr/src/app/app.sh']
args["m"]=['450M']
args["arguments"]=[user, host, application, address.strip('"'), port]
print args
launch_container(args)
