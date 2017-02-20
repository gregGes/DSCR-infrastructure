__author__ = 'gesmier'
from pymongo import MongoClient
import urllib, json

class Container(object):	
	def __init__(self):
		self.client = MongoClient() 
		self.db = self.client.manager
	
	def add_container(self, container):
		print container
		try:
			self.container = dict()
			self.container["name"] = container["name"]
			self.container["application"] = container["application"]
			self.container["location"] = container["location"]
		        self.container["containerId"] = container["containerId"] 
			self.container["memory"] = container["memory"]
		except KeyError, e:
			if e[0] is "name":
				print "error missing name"
				return
			if e[0] is "application":
				print "error missing application"
				return
			pass
		self.db.container.insert(self.container)	
		return
	
	def get_container(self, container):
		return self.db.container.find(container)
	
	def get_all(self):
		return self.db.container.find()
	
	def update_memory(self, container, memory):
		if self.exist(container):
			self.db.container.update({"name":container["name"]},{"$set": {"memory": memory}})
			return
		
	def exist(self, container):
			if self.get_container(container).count() > 0:
				return True
			else:
				return False

	def remove_container(self, container):
		self.db.container.remove(container)

class Instance(object):
	def __init__(self):
		self.client = MongoClient() 
		self.db = self.client.manager
		
	def add_instance(self, instance):
		try:
			self.instance = dict()
			self.instance["name"] = instance["name"]
			self.instance["ip"] = instance["ip"]	
			self.instance["cloud"] = instance["cloud"]
			self.instance["flavour"] = "medium"
			self.instance["availability"] = instance["availability"]
			self.instance["size"] = instance["availability"]
			self.instance["critical"] = (instance["availability"] * 10 ) / 100
		except KeyError:
			raise
			print "error parameter"
			
		self.db.instance.insert(self.instance)
		return 
	
	def exist(self, instance):
			if self.get_instance(instance).count() > 0:
				return True
			else:
				return False	

	def get_instance(self, instance):
		return self.db.instance.find(instance)

	def get_all(self):
		return self.db.instance.find()
	
	def update_availability(self, instance, availability):
		if self.exist(instance):

			self.db.instance.update({"name":instance["name"]},{"$set":{"availability":availability}})
			return
	def remove_instance(self, instance):
		self.db.instance.remove(instance)

class ImageContainer(object):
	def __init__(self):
		self.client = MongoClient()
		self.db = self.client.manager
	
	def add_image(self, image):
		try:
			self.image = dict()
			self.image["name"] = image["name"]
			self.image["limit"] = image["limit"]
			self.image["critical"] = ( image["limit"] * 10) / 100
		except KeyError:
			print "error parameter"
			return
		self.db.imagecontainer.insert(self.image)
		return
		
	def exist(self, image):
		if self.get_image(image).count() >0:
			return True
		else:
			return False
	
	def get_image(self, image):
		return self.db.imagecontainer.find(image)

	def get_all(self):
		return self.db.imagecontainer.find()

	def edit_virtual_size(self, image, usage):
		if self.exist(image):
			self.db.imagecontainer.update({"name":image["name"]},{"$set":{"limit":usage}})
			
	def remove_image(self, image):
		self.db.imagecontainer.remove(image)

class Client(object):
	def __init__(self):
		self.client = MongoClient()
		self.db = self.client.manager
	
	def add_client(self, client):
		try:
			self.client["name"] = client["name"]
			self.client["domain"] = client["domain"]
			self.client["membership"] = client["membership"]
			self.client["containers"] = client["containers"]
		except KeyError:
			print "error parameter"
			return
		self.db.clients.insert(self.client)
	
	def exist(self, client):
		if self.get_client(client).count() >0:
			return True
		else:
			return False
	
	def get_client(self, client):
		return self.db.clients.find(client)

	def get_all(self):
                return self.db.clients.find()		

	def update_clients_containers(self, client, container):
		if self.exist(client):
			if self.get_client(client).count() is 1:
				print "greg's amazing"
				if container not in self.get_client(client):
					print "greg's not that smart"
					self.db.clients.update({"name":client["name"]},{"$push":{"containers":container}})
			else:
				print "too many clients with same name"
				exit(1)
		else:
			print "doesn't exist"
