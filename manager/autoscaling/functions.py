#!/usr/bin/python

from Cloudbroker import Service
from Cloudbroker import BasicData
from Cloudbroker import Instance as instance
from Cloudbroker import CloudbrokerJob
from Cloudbroker import CBError
from Cloudbroker import CloudbrokerConnection

from subprocess import call
from Interaction import Actions
from Interaction import Updating

from Information import Information

from Scaling import Scaling
import os
import time 
import subprocess
import xml.etree.ElementTree as ElT
import pickle
import datetime

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
        if args["I"] is False:
                with open(bas_data.picklefile, "r") as pf:
                        while True:
                                try:
                                        foo = pickle.load(pf)
                                        handlers.append(foo)
                                except EOFError:
                                        break

        s_app = s_cloud = s_flavour = None

        try:
                s_app = bas_data.applications[args["application"][0]]
        except KeyError:
                print "Unknown app %s" % service
                exit(1)
        try:
                s_cloud = bas_data.clouds[args["cloud"][0]]
        except KeyError:
                print "Unknown cloud %s" % cloud
                exit(1)

        try:
                s_flavour = bas_data.clouds[args["cloud"][0]].flavours[args["flavour"][0]]
        except KeyError:
                print "Unknown flavour %s" % flavour
                exit(1)

        service_to_run = Service(s_app, s_cloud, s_flavour)
        instance_to_run = instance(service_to_run, None, args["files"])
        if args["name"][0] is not None:
                cb_handler = CloudbrokerJob(bas_data, instance_to_run, args["tag"][0], args["name"][0])
        else:
                cb_handler = CloudbrokerJob(bas_data, instance_to_run, args["tag"][0])
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
        return
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
		if job.tag == args["tag"][0]:
			job.stop_job()
			job.wait_until_complete()
			return

def listing(args):
	if args["instance"] is True and ( args["containers"] is True or args["all"] is True):
		print "instance paramenter doesn't work with containers and all"
		exit(1)
	if args["containers"] is True and args["all"] is True: 
		call(['docker', '-H', manager_ip, 'ps', '-a'])
		return
	if args["containers"] is True  and  args["all"] is False:
		call(['docker', '-H', manager_ip, 'ps'])
		return
	if args["instance"] is True:
		call(['consul', 'members'])
		return
	if args["docker"] is True:
		call(['docker', '-H', manager_ip, 'images'])
		return

def container_quit(args):
	try:
		if args["rm"] is True:
			for pointer in xrange(len(args["name"])):
				call(['docker','-H', manager_ip,'kill',args["name"][pointer]])
		        container_remove(args)
			return
		else:
			for pointer in xrange(len(args["name"])):
				call(['docker','-H', manager_ip,'kill',args["name"][pointer]])
			return
	except KeyError:	
		print "missing arguments"
		exit(1)

def container_build(args):
	try:
		if args["name"][0].startswith("container-", 0, 10):
 			if os.path.exists(args["filename"][0]):
				fileJson='{"ID":"'+args["name"][0]+'", "Service":"image-containers", "Name":"image-containers", "Tags":["'+args["filename"][0]+'"], "Address":"'+ip+'", "Port":80}'
				call(['curl', '--data', fileJson, 'http://localhost:8500/v1/agent/service/register']) 	
				return
			else:
				print "this file doesn't exist"
				exit(1)
		else:
			print "the name of the image doesn't start with container-*"
			exit(1)
	except KeyError:	
		print "missing arguments"
		exit(1)

def launch_container(args):
	command = []
	command.append('docker')
	command.append('-H')
	command.append(manager_ip)
	command.append('run')
	now = time.strftime("%d%m%y%H%M%S")	
	if Actions().check_for_launch({"name":args["image"][0]}):	
		pass
	else:
		instance = dict()
		instance["cloud"] = ["CloudSigma"]
		instance["flavour"] = ["Small"]
		instance["name"] = ["application"]
		instance["application"] = ["Node"]
		instance["files"] = ["/opt/manager_DSCR/swarm.token"]
		instance["I"] = False
		instance["tag"] = ["automatic"]
		running_instance = Actions().get_num_nodes()
		start_instance(instance)
		print instance
		Actions().wait_for_instance(running_instance) 	
	try:
                service_tags =  'SERVICE_TAGS='+args["name"][0]+'_'+args["image"][0]
                name =  args["name"][0]+'_'+args["image"][0]+'_'+now
        except KeyError:
                print "missing argument NAME or IMAGE"
                exit(1)
	
	if "location" in args:
               	constraint = 'constraint:role=='+args["location"][0]

		if args["location"][0] == "application":
			try:
				if args["domain"] != None :
					command.append('-e')
					domain_tag = 'SERVICE_TAGS='+args["domain"][0]
					command.append(domain_tag)
					###TODO see if we can add other service tag without breaking the proxy###
					#command.append('-e')
					#command.append(service_tags)
				else:
					print "no domain set"
					command.append('-e')
                			command.append(service_tags)
			except KeyError:
				print "no domain set"
                       	 	command.append('-e')
                	       	command.append(service_tags)
		else:	
			command.append('-e')
			command.append(service_tags)

	elif "relocate" in args:
		constraint = 'constraint:host=='+args["relocate"][0]
     	else:
		print "Location or relocate not defined"
		exit(1)
#	try:
#		service_tags =  'SERVICE_TAGS='+args["name"][0]+'_'+args["image"][0]
#		name =  args["name"][0]+'_'+args["image"][0]+'_'+now
#	except KeyError:
#		print "missing argument NAME or IMAGE"
#		exit(1)
#
	command.append('-e')
	command.append(constraint)
	try:
		if args["m"] != None:
			command.append('-m')
			command.append(args["m"][0])
	except (KeyError, TypeError):
		print "no memory limit set"

	try:
		for i in xrange(len(args["environment"])):
			command.append('-e')
			command.append(args["environment"][i])
	except (KeyError, TypeError):
		print "no argument ENVIRONMENT set"
	
	try:
		if args["port"] != None:
			command.append('-p')
			command.append(args["port"][0])
		else:
			print "no port set, random port"
			command.append('-P')
	except (KeyError, TypeError):
		print "no port set, random port"
                command.append('-P')
	try:
		if args["script"] != None:	
			command.append('--entrypoint')
			command.append(args["script"][0])
	except KeyError:
		print "No script"
	try:
		if args["memory"] is not None:
			command.append('--memory')
			command.append(args["memory"][0])
	except (KeyError, TypeError):
		print "no memory limit issued"		

#	if args["location"][0] == "application":
#		try:
#			if args["domain"] != None :
#				command.append('-e')
#				domain_tag = 'SERVICE_TAGS='+args["domain"][0]
#				command.append(domain_tag)
				###TODO see if we can add other service tag without breaking the proxy###
				#command.append('-e')
				#command.append(service_tags)
#			else:
#				print "no domain set"
#				command.append('-e')
 #               		command.append(service_tags)
#		except KeyError:
#			print "no domain set"
 #                       command.append('-e')
  #                      command.append(service_tags)
#	else:
#		command.append('-e')
#		command.append(service_tags)

	
	command.append('--name')
	command.append(name)
	command.append('-d')
	command.append(args["image"][0])	
	
	try:
		for i in xrange(len(args["arguments"])):
                        args["arguments"][i] = args["arguments"][i].replace("/-","-")
		command.extend(args["arguments"])
	except (KeyError,TypeError):
		print "no Argments"

	print command
	return subprocess.check_output(command).rstrip()
		

		
def get_info(args):
	address = "http://"+ip+":8500/v1/catalog"
	try:
		if args["service"] != None and args["all"] is False:
			call(['curl', address+'/service/'+args["service"][0]])
			return
		elif args["service"] == None and args["all"] is True:
			call(['curl', address+'/services'])
			return
		else:
			print "can't have both parameters"
			exit(1)	
	except KeyError:	
		print "missing arguments"
		return
	
def container_logs(args):
	try:
		if "follow" in args and args["follow"] is True:
			call(['docker', '-H', manager_ip, 'logs', '-f', args["name"][0]])
		if "name" in args:
			call(['docker', '-H', manager_ip, 'logs', args["name"][0]])
		else:	
			print "wrong arguments"
			return
	except KeyboardInterrupt:	
		exit(0)
def container_remove(args):
	try:
		if args["image"] is False:
			for pointer in xrange(len(args["name"])):
				call(['docker','-H', manager_ip,'rm',args["name"][pointer]])
			return
		elif args["image"] is True:
			for pointer in xrange(len(args["name"])):
				call(['docker', '-H', manager_ip, 'rmi', args["name"][pointer]])
               			call(['curl', 'http://localhost:8500/v1/agent/service/deregister/'+args["name"][pointer]])
				Updating().update_containers()
			return
	except Exception, e:
		if e[0] is "image" :
			for pointer in xrange(len(args["name"])):
				call(['docker','-H', manager_ip,'rm',args["name"][pointer]])
			return
		else:
			print "missing arguments"
			return
		

def container_execute(args):
	try:
		call(['docker', '-H', manager_ip, 'exec', '-it', args["name"][0]]+args["command"])
		return
	except KeyError:	
		print "missing arguments"
		exit(1)

def copy_file(args):
	try:
		if args["way"][0] == "to":
			path = args["container"][0]+":"+args["path"][0]
			call(['docker', '-H', manager_ip, 'cp', args["file"][0], path])
			return
		if args["way"][0] == "from":
			path = args["container"][0]=":"+args["file"][0]
			call(['docker', '-H', manager_ip, 'cp', path, args["path"][0]])
			return
	except KeyError:
		print "missing argument"
		exit(1)

def start_container(args):
	try:
		call(['docker', '-H', manager_ip, 'start']+args["name"])
		return
	except KeyError:
		exit(1)

def get_stats(args):
	try:
		if "no" not in args:
			if "name" in args:
                		call(['docker', '-H', manager_ip, 'stats', '--no-stream']+args["name"])
			if "all" in args and args["all"] is True:
				command= "docker -H "+manager_ip+" stats '--no-stream' $(docker -H "+manager_ip+" ps | awk '{if(NR>1) print $NF}')"
      				subprocess.call(command, shell=True)
		else:
			if "name" in args:
                		call(['docker', '-H', manager_ip, 'stats']+args["name"])
			if "all" in args and args["all"] is True:
				command= "docker -H "+manager_ip+" stats $(docker -H "+manager_ip+" ps | awk '{if(NR>1) print $NF}')"
      				subprocess.call(command, shell=True)
			
	except KeyboardInterrupt:
		exit(0)

		
def scale_down():
	result = Scaling().relocation_possible()
	print result
	if result:
		for container in result:
			print container
			test = result[container]
			if test["application"] == "mongo":
				relocate_mongo(test, container)
			elif test["application"] == "container-default":
				relocate_container(test, container)
	else:
		print "cannot scale down"

def dump_mongo(name, ip, port):
	call(['mongodump', '--host', str(ip), '--port', str(port), '-o', '/tmp/'+str(name)])
def restore_mongo(name, ip, port):
	call(['mongorestore', '--host', str(ip), '--port', str(port), '/tmp/'+str(name)])
	call(['rm', '-rf', '/tmp/'+name])

def relocate_mongo(args, container):
	argument = dict()
	argument["image"] = [str(args["application"])]
	argument["relocate"] = [str(args["relocate"])]
	client = container[(container.index("/OpenFoam/")+ len("/OpenFoam/")):container.index("_"+args["application"])]
	argument["name"] = [client]
	argument["argument"] = ["/--smallfiles"]
	print "dump database"
	dump_mongo(client, args["ip"], args["port"])
	new = launch_container(argument)
	mongo = Information(new)
	restore_mongo(client, mongo.get_ip(), mongo.get_port())
	print "restore to new database"

def relocate_container(args, container):
	argument = dict()
	argument["image"] = [args["application"]]
	argument["relocate"] = [args["relocate"]]
	client = container[(container.index("/OpenFoam/")+ len("/OpenFoam/")):container.index("_"+args["application"])]
	argument["name"] = [client]
	container = Information(args["Id"])
	argument["argument"] = [container.get_cmd()]
	launch_container(argument)
