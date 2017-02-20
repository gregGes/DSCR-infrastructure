#!/usr/bin/python
from Datamanager import Container
from Datamanager import Instance

class Scaling(object):
	def __init__(self):
		self.container = Container()
		self.instance = Instance()

	def listing(self):
		memory=0
		self.info = dict()
		for instance in self.instance.get_all():
			self.info[instance["name"]] = {}
			self.info[instance["name"]]["availability"] = instance["availability"]
			self.info[instance["name"]]["containers"] = []
			for container in self.container.get_all():
				if instance["ip"] == container["location"]:
				#	print "yes container running on this instance"
				#	print container["name"]
					name = container["name"][0]
					print container
					self.info[instance["name"]]["containers"].append({"id": container["containerId"], "name":container["name"][0],"size":container["memory"],"application":container["application"], "location": container["location"], "port":container["port"]})
		return self.info			
	
	def get_least(self):
		previous_least=None
		listing = self.listing()
		for instance in listing:
			if previous_least is None:
				previous_least=listing[instance]
				previous_least_availability = listing[instance]["availability"]
				#print  "first instance: "+ previous_least["name"]+ " availability :" + previous_least_availability
				#print ""
			else:
				#print ""
				#print "name: "+listing[instance]["name"] +" availability: "+listing[instance]["availability"]
				if listing[instance]["availability"] > previous_least_availability:
					
					previous_least = listing[instance]
					previous_least_availability = listing[instance]["availability"]
				else:
					pass
				pass
		return previous_least
	
	def get_memory_least(self):
		least = self.get_least()
		memory = 0
		for cont in xrange(len(least["containers"])):
			memory = memory + least["containers"][cont]["size"]
	
		return memory 
			
	def get_availability_left(self):
		listing = self.listing()
		least = self.get_least()
		availability = 0 

		for instance in listing:
			if listing[instance] != least:
				availability=availability+listing[instance]["availability"]				

		print availability
	
	def scalable_down(self):
		if self.get_availability_left() < self.get_memory_least():
			return True
		else: 
			return False
	
	def relocation_possible(self):
		listing = self.listing()
		least = self.get_least()
		decompted = False
		if self.scalable_down():
			not_least = dict()
			for instance in listing:
				if listing[instance] != least:
	#				print instance
	#				print listing[instance]
					not_least[instance] = listing[instance]["availability"]
			#for container in least["containers"]:
			#	container["size"]
			#print "NOT LEAST"
	#	print not_least
	#	print ""	
		result = dict()
		print least
		print least["containers"]
		print ""
		for container in least["containers"]:
			decompted = False
			last = len(not_least) - 1
			print container
			print ""
			for i, other in enumerate(not_least):
				print container["application"]+" "+container["name"]
				print container["size"]
				print not_least[other]
				print not_least[other] > container["size"]
				print ""
				if not_least[other] > container["size"]:
				 	result[container["name"]]= {"application": container["application"], "port": container["port"], "ip": container["location"], "relocate": other}
					not_least[other] = not_least[other] - container["size"]
					decompted = True
					break
				else:
					print i
					if i is last:
						print "last instance to be able to relocate the container has not enough memory"
						return False	
					pass
		if decompted:
			return result
		else:
			return decompted

