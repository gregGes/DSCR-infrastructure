#!/usr/bin/python

from Datamanager import Instance
from Datamanager import Container
from Datamanager import ImageContainer
from Datamanager import Client
import urllib, json
from subprocess import call
import time

class Updating(object):
	def __init__(self):
		self.info = Information()
		self.container = Container()
		self.nodes = Instance()
		self.client = Client()

	def update_containers(self):
		cont = self.info.list_containers()
		data = Container()
		container = dict()
		for i in xrange(len(cont)):
			try:
				container["name"] = cont[i]["Names"]	
				container["application"] = cont[i]["Image"]
				container["location"] = cont[i]["Ports"][0]["IP"]
				container["containerId"] = cont[i]["Id"]
				container["memory"] = self.info.usage_memory(container["containerId"])

			except IndexError:
				container["location"] = ""
			print container
			print "**********"
			if data.exist({"name":container["name"]}):
				print "container already exist"
			else:
				print "container to be added to the database"
				data.add_container(container)
		self.remove_exited_container()
	
	def update_nodes(self):
		node = self.info.list_nodes()
		data = Instance()
		instance = dict()
		for i in xrange(len(node)):
			instance["name"] = node[i]["Node"]
			instance["ip"] = node[i]["Address"]
			instance["cloud"] = "CloudSigma"
			instance["availability"] = 1700000000
			if data.exist({"name":instance["name"]}):
				print "instance already exist"
			elif "master" in instance["name"]:
				print "node manager no container to be deploy here"
			else:
				print "instance added"
				data.add_instance(instance)
		self.remove_exited_instance()
	
	def update_images(self):
		image = self.info.list_images()
		data = ImageContainer()
		im_cont = dict()
		for i in xrange(len(image)):
			im_cont["name"] = image[i]["RepoTags"][0].rsplit(':', 1)[0]
			im_cont["limit"] = image[i]["VirtualSize"]
			if data.exist({"name":im_cont["name"]}):
				print "image already exist"
			else:
				print "image added"
				data.add_image(im_cont)
	
	def update_availability(self):
		node = Instance()
		containers = Container()
		for cursor in node.get_all():
			print cursor
			availability = cursor["size"]
			for cursor_container in containers.get_container({"location":cursor["ip"]}):
				availability = availability - cursor_container["memory"]
				node.update_availability(cursor, availability)

	def update_memory(self):
		container = Container()
		
		for cursor in container.get_all():
			try:
				print cursor["containerId"]
				memory = self.info.usage_memory(cursor["containerId"])
				container.update_memory(cursor, memory)	
			except KeyError:
				print "Oops something whent wring with "+ str(cursor['name'])
	
	def remove_exited_instance(self):
		self.info = Information()
		for cursor in self.nodes.get_all():
			delete = 0
			for i in self.info.list_nodes():
				print "*******************"
				print "cursor"+ str(cursor["ip"])
				print "i[\"Address\"]"+str(i["Address"])
				print "*******************"
				
				
				if str(cursor["ip"]) == str(i["Address"]):
					print "DO NOT DELETE ADDRESS"
					delete = 0
					break
				else:
					delete = 1
			if delete is 1:
				print "delete ip"
				self.nodes.remove_instance(cursor)
			
	def remove_exited_container(self):
		self.info = Information()
		for cursor in self.container.get_all():
			delete = 0
			print "###########"
			for i in self.info.list_containers():
				print i["Names"] 
				print cursor["name"]
				print ""
				if cursor["name"] == i["Names"]:
					delete = 0
					print "do not delete container"
					break
				else:
					delete = 1
			if delete is 1:
				print "delete container"
				self.container.remove_container(cursor)
	def update_client(self):
		for cursor in self.container.get_all():
			for client in self.client.get_all():
				if client["name"] in cursor["name"][0] and cursor["name"][0] not in client["containers"]:
					print "don't exist already"
					self.client.update_clients_containers(client, cursor["name"][0])
				
			
class Information(object):
	def __init__(self):
		pass

	def list_containers(self):
		url="http://localhost:22375/v1.21/containers/json"
	        response=urllib.urlopen(url)
	        cont=json.loads(response.read())
	        return cont
	
	def usage_memory(self, container_id):
		url="http://localhost:22375/v1.21/containers/"+container_id+"/stats?stream=False"
		response=urllib.urlopen(url)
	        memory=json.loads(response.read())
		print "I'm here and the memory is "+ str(memory["memory_stats"]["usage"])
		return memory["memory_stats"]["usage"]
	
	def list_nodes(self):
		url="http://localhost:8500/v1/catalog/nodes"
		response=urllib.urlopen(url)
		data=json.loads(response.read())
		return data
	
	def list_images(self):
		url = "http://localhost:22375/v1.21/images/json"
		response = urllib.urlopen(url)
		data = json.loads(response.read())
		return data
	
class Actions(object):
	def __init__(self):
		self.updating = Updating()
		self.nodes = Instance()
		self.image = ImageContainer()
		self.client = Client()	
	def check_for_launch(self, args):
		limit = 0
		if self.image.exist(args):
			for im in self.image.get_image(args):
				limit = im["limit"] + im["critical"]
				break
		
		for cursor in self.nodes.get_all():
			availability = cursor["availability"] - cursor["critical"]
			if availability > limit:
				print availability
				print limit
				return True
		return False

	def remove_client(self, client):
		if self.client.get_client({"name": client}) == 1:	
			for i in self.client.get_client({"name": client}):
				for j in i["containers"]:
					self.stop(j)

	def wait_for_instance(self, initial):	
		while self.nodes.get_all().count() is initial:
			self.updating.update_nodes()
			time.sleep(2)
		return
	
	def get_num_nodes(self):
		return self.nodes.get_all().count()	
