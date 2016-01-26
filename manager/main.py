#!/usr/bin/python

from Cloudbroker import Service
from Cloudbroker import BasicData
from Cloudbroker import Instance
from Cloudbroker import CloudbrokerJob
from Cloudbroker import CBError
from Cloudbroker import CloudbrokerConnection

from subprocess import call

import os
import time 

import xml.etree.ElementTree as ElT
import pickle
import datetime
import argparse

global manager_ip
global ip

def get_manager_ip():
	p = os.popen("consul members | grep master | awk -F ' ' '{print $2}' | awk -F ':' '{print $1}'")
	s = p.readline().rstrip('\n')
	p.close()
	#print s
	return s
ip = get_manager_ip() 
manager_ip = "tcp://"+ip+":22375"

bas_data = BasicData("https://cloudsme-prototype.cloudbroker.com",
                     "/opt/manager_DSCR/inputs/cbcredentials",
                     "/opt/manager_DSCR/outputs/pickled",
                     "/opt/manager_DSCR/cloudsetup.xml")

#def start_instance(service, cloud, flavour, tag, name=None, filelist=None):
def start_instance(args):
	"""
	:param service: Application to run
	:param cloud: Cloud provider
	:param flavour: Instance size
	:param tag: free from tag to mark the launch instance
	:param filelist: list of Cloudbroker job parameter files. Optional.
	"""
	handlers = []
	if args.I is False:
		with open(bas_data.picklefile, "r") as pf:
			while True:
				try:
					foo = pickle.load(pf)
					handlers.append(foo)
				except EOFError:
					break
 
	s_app = s_cloud = s_flavour = None

	try:
		s_app = bas_data.applications[args.application[0]]
	except KeyError:
		print "Unknown app %s" % service
		exit(1)
	try:
		s_cloud = bas_data.clouds[args.cloud[0]]
	except KeyError:
		print "Unknown cloud %s" % cloud
		exit(1)

	try:
		s_flavour = bas_data.clouds[args.cloud[0]].flavours[args.flavour[0]]
 	except KeyError:
		print "Unknown flavour %s" % flavour
		exit(1)

	service_to_run = Service(s_app, s_cloud, s_flavour)
	instance_to_run = Instance(service_to_run, None, args.files)
	if args.name[0] is not None:
		cb_handler = CloudbrokerJob(bas_data, instance_to_run, args.tag[0], args.name[0])
	else:
		cb_handler = CloudbrokerJob(bas_data, instance_to_run, args.tag[0])
	try:
		cb_handler.create_job()
		res = cb_handler.launch_job()
		handlers.append(cb_handler)
		if res is not None:
			next_argument = res
	except CBError:
		print "fail"

	print datetime.datetime.now()
	with open(bas_data.picklefile, "w") as pf:
		for pclass in handlers:
			pickle.dump(pclass, pf)
	exit(0)

def stop_instance(args):
	handlers = []
	with open(bas_data.picklefile, "r") as pf:
		while True:
			try:
				foo = pickle.load(pf)
				handlers.append(foo)
			except EOFError:
				break
	print handlers
	for job in handlers:
		if job.tag == args.tag[0]:
			job.stop_job()
			job.wait_until_complete()
			exit(0)

def listing(args):
	if  args.containers is True and args.all is True: 
		call(['docker', '-H', manager_ip, 'ps', '-a'])
		exit(0)
	if  args.containers is True  and  args.all is False:
		call(['docker', '-H', manager_ip, 'ps'])
		exit(0)
	if  args.instance is True:
		call(['consul', 'members'])
		exit(0)

def container_quit(args):
	if args.rm is True:
		call(['docker','-H', manager_ip,'kill',args.name[0]])
	        container_remove(args)
		exit(0)
	else:
		call(['docker','-H', manager_ip,'kill',args.name[0]])
		exit(0)

def container_build(args):
	if args.name[0].startswith("container-", 0, 10):
 		if os.path.exists(args.filename[0]):
			call(['docker','cp',args.filename[0], 'http:/usr/local/apache2/htdocs'])
			fileJson='{"ID":"'+args.name[0]+'", "Service":"containers", "Name":"containers", "Tags":["'+args.filename[0]+'"], "Address":"'+ip+'", "Port":80}'
			call(['curl', '--data', fileJson, 'http://localhost:8500/v1/agent/service/register']) 	
			exit(0)
		else:
			print "this file doesn't exist"
			exit(1)
	else:
		print "the name of the image doesn't start with container-*"
		exit(1)

def launch_container(args):
	command = []
	command.append('docker')
	command.append('-H')
	command.append(manager_ip)
	command.append('run')
	
	now = time.strftime("%d%m%y%H%M%S")	
	constraint = 'constraint:role=='+args.location[0]
	service_tags =  'SERVICE_TAGS='+args.name[0]+'_'+args.image[0]
	name =  args.name[0]+'_'+args.image[0]+'_'+now
	command.append('-e')
	command.append(constraint)
	if args.environment != None:
		for i in xrange(len(args.environment)):
			command.append('-e')
			command.append(args.environment[i])
	if args.port != None:
		command.append('-p')
		command.append(args.port[0])
	else:
		command.append('-P')

	if args.script != None:
		command.append('--entrypoint')
		command.append(args.script[0])

	if args.location[0] == "application":
		if args.domain != None :
			command.append('-e')
			domain_tag = 'SERVICE_TAGS='+args.domain[0]
			command.append(domain_tag)
			
	else:
		command.append('-e')
		command.append(service_tags)

	command.append('--name')
	command.append(name)
	command.append('-d')
	command.append(args.image[0])	
	
	if args.arguments != None:
		for i in xrange(len(args.arguments)):
			args.arguments[i] = args.arguments[i].replace("/-","-")
		command.extend(args.arguments)

	print command
	call(command)
	exit(0)

		
def get_info(args):
	address = "http://"+ip+":8500/v1/catalog"
	if args.service != None and args.all is False:
		call(['curl', address+'/service/'+args.service[0]])
		exit(0)
	elif args.service == None and args.all is True:
		call(['curl', address+'/services'])
		exit(0)
	else:
		print "can't have both parameters"
		exit(1)	
	
def container_logs(args):
	call(['docker', '-H', manager_ip, 'logs', args.name[0]])
	exit(0)

def container_remove(args):
	call(['docker','-H', manager_ip,'rm',args.name[0]])
	exit(0)

def container_execute(args):
	call(['docker', '-H', manager_ip, 'exec', '-it', args.name[0]]+args.command)
	exit(0)

def copy_file(args):
	if args.way[0] == "to":
		path = args.container[0]+":"+args.path[0]
		call(['docker', '-H', manager_ip, 'cp', args.file[0], path])
		exit(0)
	if args.way[0] == "from":
		path = args.container[0]=":"+args.file[0]
		call(['docker', '-H', manager_ip, 'cp', path, args.path[0]])
		exit(0)


parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()

parser_start = subparsers.add_parser('start', help="this will start a new instance")
parser_stop = subparsers.add_parser('stop', help="this will stop a defined instance")
parser_launch = subparsers.add_parser('launch', help="this will launch a container")
parser_quit = subparsers.add_parser('quit', help="this will stop a running container")
parser_list = subparsers.add_parser('list', help="this will list containers/instances")
parser_build = subparsers.add_parser('build', help="this will build the image in each databases instances and applications instances running")
parser_info = subparsers.add_parser('info', help="this will gives info on the services running on the infrastructure")
parser_logs = subparsers.add_parser('logs', help="this will allow to check the logs of a container")
parser_remove = subparsers.add_parser('remove', help="this will remove the non runing container")
parser_exec = subparsers.add_parser('execute', help="this will execute the command given on the container")
parser_copy = subparsers.add_parser('copy', help="this will copy files inside a container")

parser_start.add_argument("-c", "--cloud", nargs=1, required=True, help="cloud")
parser_start.add_argument("-a", "--application", nargs=1, required=True, help="instance")
parser_start.add_argument("-f", "--flavour", nargs=1, required=True, help="flavour")
parser_start.add_argument("-t", "--tag", nargs=1, required=True, help="tag")
parser_start.add_argument("-n", "--name", nargs=1, choices=["application", "database"], required=True, help="service tag")
parser_start.add_argument("files", metavar="filename", nargs="*", help="input file names")
parser_start.add_argument("-I", action="store_true", help="init instances")
parser_start.set_defaults(func=start_instance)

parser_stop.add_argument("-t", "--tag", nargs=1, required=True, help="service tag")
parser_stop.set_defaults(func=stop_instance)

parser_list.add_argument("-i", "--instance", action='store_true', help="list instances")
parser_list.add_argument("-c", "--containers", action='store_true', help="list containers")
parser_list.add_argument("-a", "--all", action='store_true', help="list all containers")
parser_list.set_defaults(func=listing)

parser_build.add_argument("-n", "--name", nargs=1, required=True, help="image name, (should match the name of the directory where the file to build are located and should be as container-name)")
parser_build.add_argument("-f", "--filename", nargs=1, required=True, help="tarball name containing the directory where the Dockerfile and all oter file needed are")
parser_build.set_defaults(func=container_build)


parser_quit.add_argument("-n","--name", nargs=1, required=True, help="name of the container")
parser_quit.add_argument("-rm", action='store_true', help="remove the container after it stopped")
parser_quit.set_defaults(func=container_quit)

parser_launch.add_argument("-i", "--image", nargs=1, required=True, help="image name")
parser_launch.add_argument("-n", "--name", nargs=1, required=True, help="client name")
parser_launch.add_argument("-l", "--location", nargs=1, required=True, help="on which instance to run the container")
parser_launch.add_argument("-s", "--script", nargs=1, help="location of the script inside the container")
parser_launch.add_argument("-d", "--domain", nargs=1, help="domain name")
parser_launch.add_argument("-a", "--arguments", nargs="*", help="arguments to pass to the container")
parser_launch.add_argument("-p", "--port", nargs=1, help="run the container on a specific port")
parser_launch.add_argument("-e", "--environment", action='append', help="add an environment variable")
parser_launch.set_defaults(func=launch_container)

parser_info.add_argument("-s", "--service", nargs=1, help="name of the services to get the info")
parser_info.add_argument("-a", "--all", action='store_true', help="list of all the services running")
parser_info.set_defaults(func=get_info)

parser_logs.add_argument("-n", "--name", nargs=1, required=True, help="container name")
parser_logs.set_defaults(func=container_logs)

parser_remove.add_argument("-n", "--name", nargs=1, required=True, help="container name")
parser_remove.set_defaults(func=container_remove)

parser_exec.add_argument("-n", "--name", nargs=1, required=True, help="container name")
parser_exec.add_argument("-c", "--command", nargs="*", required=True, help="command to pass to the container")
parser_exec.set_defaults(func=container_execute)

parser_copy.add_argument("-f", "--file", nargs=1, required=True, help="full path of the file to copy")
parser_copy.add_argument("-p", "--path", nargs=1, required=True, help="path to copy the file to")
parser_copy.add_argument("-c", "--container", nargs=1, required=True, help="container wanted")
parser_copy.add_argument("-w", "--way", nargs=1, choices=["from", "to"], required=True, help="copy from or to the container")
parser_copy.set_defaults(func=copy_file)

args = parser.parse_args()
args.func(args)


exit(1)
