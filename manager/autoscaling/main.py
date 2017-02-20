#!/usr/bin/python

from functions import *

import argparse


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
parser_list.add_argument("-d", "--docker", action='store_true', help="list all the images on the infrastructures")
parser_list.set_defaults(func=listing)

parser_build.add_argument("-n", "--name", nargs=1, required=True, help="image name, (should match the name of the directory where the file to build are located and should be as container-name)")
parser_build.add_argument("-f", "--filename", nargs=1, required=True, help="tarball name containing the directory where the Dockerfile and all oter file needed are")
parser_build.set_defaults(func=container_build)


parser_quit.add_argument("-n","--name", nargs="*", required=True, help="name of the container")
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
parser_logs.add_argument("-f", "--follow", action='store_true', help="stream continously the logs")
parser_logs.set_defaults(func=container_logs)

parser_remove.add_argument("-n", "--name", nargs="*", required=True, help="container name")
parser_remove.add_argument("-i", "--image", action='store_true', help="docker image to remove")
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
args.func(vars(args))


exit(1)
