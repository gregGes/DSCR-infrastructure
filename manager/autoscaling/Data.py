__author__ = 'gesmier'
from pymongo import MongoClient
import urllib, json

class Container(object):
        # initialisation to use the database
        def __init__(self):
                self.client = MongoClient()
                self.db = self.client.manager

        def add_container(self, c):
                try:
                        self.container = dict()
                        self.container["name"] = c["name"]
                        self.container["application"] = c["application"]
                        self.container["location"] = c["location"]
                        self.container["memory"] = c["memory"]
                except KeyError:
                        print "error parameter"
                        exit(1)
                self.db.container.insert(self.container)
                return
        def get_container(self, c):
                return self.db.container.find(c)
        def get_container():
                return self.db.container.find()
class Instance(object):
        # initialisation to use the database
        def __init__(self, i):
                client = MongoClient()
                db = client.manager
                try:
                        self.instance = dict()
                        self.instance["name"] = i["name"]
                        self.instance["ip"] = i["ip"]
                        self.instance["cloud"] = i["cloud"]
                        self.instance["flavour"] = "medium"
                        self.instance["availability"] = i["availibility"]
                except KeyError:
                        print "error parameter"
                        exit(1)
                db.instance.insert(self.instance)

