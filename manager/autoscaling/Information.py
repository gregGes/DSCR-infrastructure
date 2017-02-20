#!/usr/bin/python
import urllib, json

class Information(object):
	
	def __init__(self, _id):
		self.url="http://localhost:22375/v1.21/containers/json"
		self.response=urllib.urlopen(self.url)
		self.container=json.loads(self.response.read())
		self.Id = _id	
		
	def get_ip(self):
		for i in xrange(len(self.container)):
			if self.container[i]["Id"] == self.Id:
				return str(self.container[i]["Ports"][0]["IP"])
			else:
				pass
	def get_port(self):
		for i in xrange(len(self.container)):
			if self.container[i]["Id"] == self.Id:
				return self.container[i]["Ports"][0]["PublicPort"]
			else:
				pass
	def to_string(self):
		for i in xrange(len(self.container)):
                        if self.container[i]["Id"] == self.Id:
                                return self.container[i]
			else:
				pass
	def get_cmd(self):
		for i in xrange(len(self.container)):
                        if self.container[i]["Id"] == self.Id:
				return str(self.container[i]["Command"])
			else:
				pass
