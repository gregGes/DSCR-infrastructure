#!/usr/bin/python

import yaml
import sys
sys.path.append('/opt/manager_DSCR')
from functions import launch_container

file_name = sys.argv[1]
available_command={"image", "name", "location", "script", "domain", "arguments", "port", "environment"}
mandatory_command={"image", "name", "location"}
## check if dictionary has keys that belongs to available command.
def check_list(args):
	for pointer in xrange(len(args)):
		if not all(key in args[pointer] for key in mandatory_command):
			raise Exception("missing a mandatory command")
		if not all(key in available_command for key in args[pointer]):
			raise Exception("command are not all belonging to the available command")
		for element in args[pointer]:
                	args[pointer][element]=make_list(args[pointer][element])
	return args


## this will make the input into a 
## list if it's not in the first place
def make_list(x):
	if isinstance(x, list):
		return x
	else:
		return [x]


## launch the container 
def launch(args):
	print args
	print "launching "+args["name"][0]
	launch_container(args)

## open the and load the data of the input file
with open(file_name,'r') as f:
		doc = yaml.load(f)

## check if first key is containers
if "containers" in doc:
	containers = check_list(doc["containers"])
	print containers
	print "*******"
	for pointer in xrange(len(containers)):
		launch(containers[pointer])
	exit(0)
else:
	exit(1)

