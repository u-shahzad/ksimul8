#!/usr/bin/env python

from rich import table
from rich import console
from cluster import Cluster
from node import Node
from kubescheduler import Kubescheduler
from createPod import CreatePod
from rich.console import Console
from rich.table import Table
from rich.traceback import install
from rich.markdown import Markdown
from rich.progress import track
from random import randint
import simpy
import queue
import logging
import yaml
import glob
import os
import time
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

node_table = Table(title="Final Node Description")

node_table.add_column("Name", justify="center", style="cyan")
node_table.add_column("ID", justify="center", style="magenta")
node_table.add_column("Num of Pods", justify="center", style="green")
node_table.add_column("Memory", justify="center", style="cyan")
node_table.add_column("CPU", justify="center", style="magenta")
node_table.add_column("Score", justify="center", style="green")
node_table.add_column("Port", justify="center", style="cyan")

console = Console(record=True)

'''
creates a test.log file which contains the result of the experiment performed.
'''
logging.basicConfig(filename='test.log', level=logging.DEBUG,
                    format='%(asctime)s:%(levelname)s:%(message)s')

_NODES = []  # contains list of all the working nodes in the cluster
_PODS = []  # contains list of all the pods created
_POD_QUEUE = queue.Queue()  # pod arrives in a FIFO queue


def cluster_generator(env):

    console.log("---> Start Cluster\n", style="bold green")
    cluster = Cluster(env, 1)  # create cluster with single master nodes

    '''
    Tell the simulation enviroment to run the
    create nodes activity generator
    '''
    env.process(create_nodes_generator(env, cluster))  # calling function to create nodes

    create_pods()  # create pods and add them in a FIFO queue

    # Keep doing this indefinitely (whilst the program's running)
    while True:

        # if the queue containing pods is not empty
        if (_POD_QUEUE.empty() is False):
            
            pod = _POD_QUEUE.get()  # pop the pod from the queue

            pod.arrivalTime = env.now
            logging.info(' {} entered queue at {} seconds \n'.format(
                    pod.name, pod.arrivalTime))

            '''
            Tell the simulation enviroment to run the
            kubescheduler activity generator
            '''
            env.process(kubescheduler_generator(env, cluster, pod))

            '''
            Tell the simulation enviroment to run the
            drop pod activity generator
            '''
            # env.process(drop_pod_generator(env, cluster, pod))

        # Calculate the time until the next pod arrives
        # t = random.expovariate(1.0 / pod.arrivalRate)
        t = pod.arrivalRate

        '''
        Tell the simulation to freeze this function in place
        until that sampled inter-arrival time has elapsed
        '''
        yield env.timeout(t)


def create_nodes_generator(env, cluster):

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
                        creationTime = input['cluster']['creationTime']

                        node = Node(name, memory, cpu, label)
                        cluster.add_node(node)
                        _NODES.append(node)

                except yaml.YAMLError as exc:

                    print(exc)

        yield env.timeout(creationTime)


def create_pods():

    console.log("===> Creating Pods ", style="bold blue")

    pod_data = {}  # contains pod info described in the input file

    for filename in glob.glob('src/*.yaml'):

        with open(os.path.join(os.getcwd(), filename), 'r') as stream:

            try:
                input = yaml.safe_load(stream)

                for i in track(range(len(input['pods']['pod']))):

                    pod_name = (input['pods']['pod'][i]['name'])
                    plugin  = (input['pods']['pod'][i]['plugin'])
                    arrivalRate = (input['pods']['pod'][i]['arrivalRate'])
                    serviceTime = (input['pods']['pod'][i]['serviceTime'])

                    pod_data[pod_name] = [plugin, arrivalRate, serviceTime]

            except yaml.YAMLError as exc:

                print(exc)

    createPod = CreatePod()

    pods = createPod.create(_POD_QUEUE, pod_data)

    for pod in pods:
        _PODS.append(pod)


def drop_pod_generator(env, cluster, pod):
    with cluster.master_node.request() as req:
    # with r.request() as req:
        yield req

        if pod.is_bind:
            console.log("\n===> Removing {}\n".format(pod.name),
                        style="bold red")

            pod.node.remove_pod(pod)
            pod.node = None

            logging.info(' {} removed at {} seconds \n'.format(pod.name, env.now))
            yield env.timeout(pod.serviceTime)

        else:
            console.log("\n===> {} not bind\n".format(pod.name),
                        style="bold red")
            yield env.timeout(0)


def kubescheduler_generator(env, cluster, pod):

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

        console.log("\n---> Run Kubescheduler for {}\n".format(
                    pod.name), style="bold green")
        kubescheduler = Kubescheduler()

        # Start kubescheduler
        kubescheduler.scheduling_cycle(cluster, pod)

        pod_assigned_node_time = env.now

        if pod.is_bind is True:
            logging.info(' {} assigned a node at {} seconds \n'.format(
                            pod.name, pod_assigned_node_time))

        table.add_row(pod.name, str(pod.id), pod.nodeName,
                        str(pod.memory), str(pod.cpu), str(pod.is_bind),
                        str(pod.port), str(pod.arrivalTime),
                        str(pod.serviceTime))

        console.log(table)

        scheduling_time = randint(5, 10)
        '''
        Tell the simulation to freeze this function in place until that
        sampled life time has elapsed (which is also keeping the master
        node in use and unavailable elsewhere, as we are still in
        the 'with' statement
        '''
        yield env.timeout(scheduling_time)


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

    # r = simpy.Resource(env, capacity=1)
    # for pod in _PODS:
    #     env.process(drop_pod_generator(env, r, pod))

    '''
    Set the simulation to run for 60 time units (representing minutes in
    our model, so for one hour of simulated time)
    '''
    env.run(until=simulation_time)

    MARKDOWN = """# End Result"""
    console.log(Markdown(MARKDOWN), style="bold magenta")
    
    # for node in _NODES:
    #     node_table.add_row(node.name, str(node.id), str(node.num_of_pods),
    #                         str(node.memory), str(node.cpu), str(node.score),
    #                         str(node.port))
    # console.log(node_table)

    # for pod in _PODS:
    #     table.add_row(pod.name, str(pod.id), pod.nodeName,
    #                     str(pod.memory), str(pod.cpu), str(pod.is_bind),
    #                     str(pod.port), str(pod.arrivalTime),
    #                     str(pod.serviceTime))
    # console.log(table)

    console.save_html("demo.html")


if __name__ == "__main__":
    main()
