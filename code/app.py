#!/usr/bin/env python

from rich import style, table
from rich import console
from cluster import Cluster
from pod import Pod
from node import Node
from kubescheduler import Kubescheduler
from createPod import CreatePod
from plugin import Plugin
from rich.console import Console
from rich.table import Table
from rich.traceback import install
from rich.markdown import Markdown
from rich.progress import track
import simpy
import random
import queue
import logging
import yaml
import glob
import os
import time
import asyncio
install()  # creates a better readable traceback


table = Table(title="Pod Description")

table.add_column("Name", justify="center", style="cyan")
table.add_column("ID", justify="center", style="magenta")
table.add_column("Node Name", justify="center", style="green")
table.add_column("Memory Req", justify="center", style="cyan")
table.add_column("CPU Req", justify="center", style="magenta")
table.add_column("Bind", justify="center", style="green")
table.add_column("Port", justify="center", style="cyan")
table.add_column("Arrival Time", justify="center", style="magenta")
table.add_column("Service Time", justify="center", style="green")

console = Console(record=True)

'''
creates a test.log file which contains the result of the experiment performed.
'''
logging.basicConfig(filename='test.log', level=logging.DEBUG,
                    format='%(asctime)s:%(levelname)s:%(message)s')

_NODES = []
_PODS = []


def cluster_generator(env):

    console.log("---> Start Cluster\n", style="bold green")
    cluster = Cluster(env, 1)  # create cluster with single master nodes

    env.process(create_nodes(env, cluster))  # calling function to create nodes

    pod_queue = create_pods()  # get the queue containing the pods

    console.log("\n---> Start Kubescheduler\n", style="bold green")

    # Keep doing this indefinitely (whilst the program's running)
    while True:

        if (pod_queue.empty() is False):
            '''
            Tell the simulation enviroment to run the
            kubescheduler activity generator
            '''
            pod = pod_queue.get()
            env.process(kubescheduler_generator(
                                                env, pod.serviceTime,
                                                cluster, pod))

        # Calculate the time until the next pod arrives
        # t = random.expovariate(1.0 / pod.arrivalRate)
        t = pod.arrivalRate

        '''
        Tell the simulation to freeze this function in place
        until that sampled inter-arrival time has elapsed
        '''
        yield env.timeout(t)


def create_nodes(env, cluster):

    '''
    This function creates all working nodes described in the input file.
    '''
    with cluster.master_node.request() as req:
        yield req

        console.log("===> Creating Nodes ", style="bold blue")

        for filename in glob.glob('src/*.yaml'):  # selects on .yaml extention file

            with open(os.path.join(os.getcwd(), filename), 'r') as stream:

                try:
                    input = yaml.safe_load(stream)  # loads the data in input file

                    # loop will run till it reach the final node in the list
                    for i in track(range(len(input['cluster']['node']))):

                        name = input['cluster']['node'][i]['name']
                        memory = input['cluster']['node'][i]['memory']
                        cpu = input['cluster']['node'][i]['cpu']
                        label = input['cluster']['node'][i]['label']

                        node = Node(name, memory, cpu, label)
                        cluster.add_node(node)
                        _NODES.append(node)

                except yaml.YAMLError as exc:

                    print(exc)

        yield env.timeout(2)


def create_pods():

    console.log("===> Creating Pods ", style="bold blue")

    pod_name = []
    plugin = []
    arrivalRate = []
    serviceTime = []

    pod_queue = queue.Queue()  # pod arrives in a FIFO queue

    for filename in glob.glob('src/*.yaml'):

        with open(os.path.join(os.getcwd(), filename), 'r') as stream:

            try:
                input = yaml.safe_load(stream)

                for i in track(range(len(input['pods']['pod']))):

                    pod_name.append(input['pods']['pod'][i]['name'])
                    plugin.append(input['pods']['pod'][i]['plugin'])
                    arrivalRate.append(input['pods']['pod'][i]['arrivalRate'])
                    serviceTime.append(input['pods']['pod'][i]['serviceTime'])

            except yaml.YAMLError as exc:

                print(exc)

    createPod = CreatePod()
    #plugin.reverse()
    pods = createPod.create(pod_queue, pod_name, plugin, arrivalRate, serviceTime)
    for pod in pods:
        _PODS.append(pod)

    return pod_queue


def drop_pod(pod):
    console.log("\n===> Removing Pod\n", style="bold red")
    pod.node.remove_pod(pod)
    console.log(pod.node.serialize())
    pod.node = None
    console.log(pod.serialize())


def kubescheduler_generator(env, ideal_service_time, cluster, pod):
    pod_arrival_time = env.now
    pod.arrivalTime = pod_arrival_time
    logging.info(' Pod {} entered queue at {} time unit \n'.format(
                    pod.id, pod_arrival_time))

    with cluster.master_node.request() as req:
        '''
        The function freezes in place until the request can be met
        (ie there is a node available for the request to be met).
        '''

        yield req
        '''
        Once the function unfreezes, it'll resume from here, so when we get
        to this point we know a node is now available. So we can record the
        current simulation time, and therefore work out how long
        the pod was queuing.
        '''

        kubescheduler = Kubescheduler()

        # Start kubescheduler
        kubescheduler.scheduling_cycle(cluster, pod)

        # scheduling_time = random.expovariate(1.0 / ideal_service_time)

        table.add_row(pod.name, str(pod.id), pod.nodeName,
                        str(pod.memory), str(pod.cpu), str(pod.is_bind),
                        str(pod.port), str(pod.arrivalTime), str(ideal_service_time))

        console.log(table)

        if (pod.name == 'pod5' and pod.is_bind):
            drop_pod(pod)

        '''
        Tell the simulation to freeze this function in place until that
        sampled life time has elapsed (which is also keeping the master
        node in use and unavailable elsewhere, as we are still in
        the 'with' statement
        '''
        yield env.timeout(ideal_service_time)
        pod_assigned_node_time = env.now

        if pod.is_bind is True:
            logging.info(' Pod {} assigned a node at {} time unit \n'.format(
                            pod.id, pod_assigned_node_time))


def main():
    '''
    We defined the generator functions above. Here's where we will get
    everything running. First we set up a new SimPy simulation enviroment
    '''

    for filename in glob.glob('src/*.yaml'):

        with open(os.path.join(os.getcwd(), filename), 'r') as stream:

            try:
                input = yaml.safe_load(stream)

                simulation_time = input['metadata']['simulationTime']

            except yaml.YAMLError as exc:

                print(exc)

    env = simpy.Environment()  # create a simulation environment

    MARKDOWN = """# Start Simulation"""
    console.log(Markdown(MARKDOWN), style="bold magenta")

    # Start the cluster
    env.process(cluster_generator(env))

    '''
    Set the simulation to run for 60 time units (representing minutes in
    our model, so for one hour of simulated time)
    '''
    env.run(until=simulation_time)

    MARKDOWN = """# End Result"""
    console.log(Markdown(MARKDOWN), style="bold magenta")

    # for pod in _PODS:
    #     print(pod.serialize())
    
    # for node in _NODES:
    #     print(node.serialize())

    # print("nodes len: {}".format(len(_NODES)))
    # print("pods len: {}".format(len(_PODS)))

    console.save_html("demo.html")


if __name__ == "__main__":
    main()
