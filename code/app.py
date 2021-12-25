#!/usr/bin/env python

from rich import table
from rich import console
from cluster import Cluster
from node import Node
from pod import Pod
from plugin import Plugin
from container import Container
from kubescheduler import Kubescheduler
from container import Container
from rich.console import Console
from rich.table import Table
from rich.traceback import install
from rich.markdown import Markdown
from rich.progress import track
from random import randint
import simpy.rt
import queue
import logging
import yaml
import glob
import os
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


def cluster_generator(env, num_mNode):

    console.log("---> Start Cluster *** [Simulation Time: {} seconds]\n".format(
                env.now), style="bold green")

    cluster = Cluster(env, num_mNode)
    request = cluster.master_node.request()
    yield request

    '''
    Tell the simulation enviroment to run the
    create_nodes activity generator.
    '''
    nodes = env.process(create_nodes_generator(env, cluster))
    yield  nodes
    console.log("---> Nodes created successfully *** [Simulation Time: {} seconds]\n".format(
                env.now), style="blue bold")

    '''
    Tell the simulation enviroment to run the create_pods activity generator.
    The method create pods and add them in a FIFO queue.
    '''
    pods = env.process(create_pods(env))
    yield pods

    # Keep doing this indefinitely (whilst the program's running)
    while True:

        # wait before getting next pod
        yield env.timeout(5)

        # if the queue containing pods is not empty
        if (_POD_QUEUE.empty() is False):

            pod = _POD_QUEUE.get()  # pop the pod from the queue

            '''
            Tell the simulation enviroment to run the
            kubescheduler activity generator
            '''
            scheduler = env.process(kubescheduler_generator(env, cluster, pod))

            '''
            Tell the simulation enviroment to run the
            drop pod activity generator
            '''
            removePod = env.process(drop_pod_generator(env, pod))

        yield scheduler | removePod  # either one process finished

        if scheduler.triggered and removePod.triggered:
            break

    cluster.master_node.release(request)


def create_nodes_generator(env, cluster):

    '''
    This function creates all working nodes described in the input file.
    '''

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
                    creationTime = input['cluster']['wNode_creationTime']

                    node = Node(name, memory, cpu, label)
                    cluster.add_node(node)
                    _NODES.append(node)

                    yield env.timeout(creationTime)

            except yaml.YAMLError as exc:
                print(exc)


def create_pods(env):

    console.log("===> Creating Pods ", style="bold blue")

    pod_data = {}  # contains pod info described in the input file

    for filename in glob.glob('src/*.yaml'):
        with open(os.path.join(os.getcwd(), filename), 'r') as stream:
            try:
                input = yaml.safe_load(stream)
                for i in track(range(len(input['pods']['pod']))):
                    pod_name = input['pods']['pod'][i]['name']
                    plugin  = input['pods']['pod'][i]['plugin']
                    arrivalRate = input['pods']['pod'][i]['arrivalRate']
                    serviceTime = input['pods']['pod'][i]['serviceTime']

                    pod_data[pod_name] = [plugin, arrivalRate, serviceTime]

            except yaml.YAMLError as exc:
                print(exc)

    container_list = []

    for filename in sorted(glob.glob('pods/*.yaml')):
        with open(os.path.join(os.getcwd(), filename), 'r') as stream:
            try:
                pod_file = yaml.safe_load(stream)
                name = pod_file['metadata']['name']

                if name in pod_data:
                    yield env.timeout(pod_data[name][1])
                    logging.info(' {} entered queue at {} seconds \n'.format(
                                 name, env.now))
                    console.log('---> {} entered queue at {} seconds'.format(
                                name, env.now))
                    schedulerName = pod_file['spec']['schedulerName']
                    nodeName = pod_file['spec']['nodeName']
                    nodeSelector = pod_file['spec']['nodeSelector']['disktype']
                    port = pod_file['spec']['port']

                    for i in range(len(pod_file['spec']['containers'])):
                        containerName = pod_file['spec']['containers'][i]['name']
                        image = pod_file['spec']['containers'][i]['image']
                        memory = int(pod_file['spec']['containers'][i]['resources']['limits']['memory'][:-2])
                        cpu = int(pod_file['spec']['containers'][i]['resources']['limits']['cpu'][:-1])

                        container_list.append(Container(containerName,
                                                        image, memory,
                                                        cpu))

                    pod_memory = sum(map(lambda x: x.memory, container_list))
                    pod_cpu = sum(map(lambda x: x.cpu, container_list))

                    plug = Plugin()

                    plugin_list = list(map(lambda x: x == "1", pod_data[name][0]))

                    plug.predicate_list = plugin_list[:9]
                    plug.priorites_list = plugin_list[9:]

                    pod = Pod(name, schedulerName, pod_memory, pod_cpu,
                                plug, env.now, pod_data[name][2],
                                container_list.copy(), nodeName,
                                nodeSelector, port)
                    _POD_QUEUE.put(pod)
                    _PODS.append(pod)
                    container_list.clear()

            except yaml.YAMLError as exc:
                print(exc)


def drop_pod_generator(env, pod):

    if pod.is_bind:
        yield env.timeout(pod.serviceTime)

        console.log("\n===> Removing {} *** [Simulation Time: {} seconds]".format(
                    pod.name, env.now), style="bold red")

        pod.node.remove_pod(pod)
        pod.node = None

        logging.info(' {} removed at {} seconds\n'.format(pod.name, env.now))

    else:
        console.log("\n===> Can't Remove {} because it's not bind".format(
                    pod.name), style="bold red")


def kubescheduler_generator(env, cluster, pod):

    console.log("\n---> Run Kubescheduler for {}\n".format(
                pod.name, env.now), style="bold green")
    kubescheduler = Kubescheduler()

    # Start kubescheduler
    kubescheduler.scheduling_cycle(cluster, pod, env.now)

    pod_assigned_node_time = env.now

    if pod.is_bind is True:
        logging.info(' {} assigned a node at {} seconds \n'.format(
                        pod.name, pod_assigned_node_time))

    table.add_row(pod.name, str(pod.id), pod.nodeName,
                    str(pod.memory), str(pod.cpu), str(pod.is_bind),
                    str(pod.port), str(pod.arrivalTime),
                    str(pod.serviceTime))

    console.log(table)

    scheduling_time = 5
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
                num_mNode = input['cluster']['num_mNode']

            except yaml.YAMLError as exc:
                print(exc)

    # create a simulation environment
    env = simpy.rt.RealtimeEnvironment(factor=0.01, strict=False)

    MARKDOWN = """# Start Simulation"""
    console.log(Markdown(MARKDOWN), style="bold magenta")

    cluster = env.process(cluster_generator(env, num_mNode))
    # Set the simulation to run till the cluster process finish
    env.run(until=cluster)

    MARKDOWN = """# End Result"""
    console.log(Markdown(MARKDOWN), style="bold magenta")

    for node in _NODES:
        node_table.add_row(node.name, str(node.id), str(node.num_of_pods),
                            str(node.memory), str(node.cpu), str(node.score),
                            str(node.port))
    console.log(node_table)

    for pod in _PODS:
        table.add_row(pod.name, str(pod.id), pod.nodeName,
                        str(pod.memory), str(pod.cpu), str(pod.is_bind),
                        str(pod.port), str(pod.arrivalTime),
                        str(pod.serviceTime))
    console.log(table)

    console.save_html("demo.html")


if __name__ == "__main__":
    main()
