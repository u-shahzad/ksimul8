#!/usr/bin/env python
from cluster import Cluster
from node import Node
from pod import Pod
from plugin import Plugin
from container import Container
from kubescheduler import Kubescheduler
from rich.console import Console
from rich.table import Table
from rich.traceback import install
from rich.markdown import Markdown
from rich.progress import track
from random import seed
from random import randint
from numpy import random
from functools import reduce
from tqdm import tqdm
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
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
table.add_column("Node Assigned", justify="center", style="green")
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
_POD_QUEUE = queue.Queue()  # pods arrive in a FIFO queue

index = []  # list of simulation time when pod is bind to a node
pd_pods = []  # list of names of all the pods
pd_status = []  # boolean list for the bind/unbind status of pod


def cluster_generator(env, num_mNode, num_node, jobs, jobType, printing):

    if printing:
        console.log("---> Start Cluster :hourglass: [{} seconds]\n".format(
                env.now), style="bold green")
    logging.info(' Start Cluster at {} seconds\n'.format(env.now))

    cluster = Cluster(env, num_mNode)  # create cluster with master node(s)
    request = cluster.master_node.request()  # access master node resource
    yield request

    '''
    Tell the simulation enviroment to run the
    create_nodes activity generator.
    '''
    nodes = env.process(create_nodes_generator(env, cluster, num_node, printing))
    yield nodes
    if printing:
        console.log("---> Nodes created successfully :hourglass: [{} seconds]\n".format(
                env.now), style="blue bold")
    logging.info(' Nodes created successfully at {} seconds\n'.format(env.now))

    '''
    Tell the simulation enviroment to run the create_pods activity generator.
    The method create pods and add them in a FIFO queue.
    '''
    if jobType == 'yaml':
        pods = env.process(create_pods_yaml_generator(env, printing))
    elif jobType == 'csv':
        pods = env.process(create_pods_csv_generator(env, jobs, printing))
    yield pods

    # Keep doing this indefinitely (whilst the program's running)
    while True:

        # wait before getting next pod
        yield env.timeout(5)

        # if the queue is not empty
        if (_POD_QUEUE.empty() is False):

            pod = _POD_QUEUE.get()  # pop the pod from the queue
            pod.wait_in_queue = env.now - pod.arrivalTime

            '''
            Tell the simulation enviroment to run the
            kubescheduler activity generator
            '''
            scheduler = env.process(kubescheduler_generator(env, cluster, pod, printing))

            '''
            Tell the simulation enviroment to run the
            drop pod activity generator
            '''
            removePod = env.process(drop_pod_generator(env, pod, cluster, printing))

        yield scheduler | removePod  # Either one process finished

        # Stop the cluster if the following processes finished
        if scheduler.triggered and removePod.triggered:
            break

    cluster.master_node.release(request)  # release resources


def create_nodes_generator(env, cluster, num_node, printing):
    '''
    This function creates all working nodes described in the input file.
    '''
    if printing:
        console.log("===> Creating Nodes ", style="bold blue")

    for filename in glob.glob('src/*.yaml'):  # load YAML file from src
        with open(os.path.join(os.getcwd(), filename), 'r') as stream:
            try:
                input = yaml.safe_load(stream)  # loads data from input file
                if input['cluster']['wNode_creationType'] == 'auto':
                    memory = input['cluster']['autoNode']['memory']
                    cpu = input['cluster']['autoNode']['cpu']
                    label = input['cluster']['autoNode']['label']
                    creationTime = input['cluster']['wNode_creationTime']
                    name = 'n'
                    for i in range(num_node):
                        node = Node(name+str(i), memory, cpu, cluster, label)  # create node
                        cluster.add_node(node)  # add node to the cluster
                        _NODES.append(node)

                        yield env.timeout(creationTime)

                elif input['cluster']['wNode_creationType'] == 'manual':
                    for i in range(num_node):
                        name = input['cluster']['node'][i]['name']
                        memory = input['cluster']['node'][i]['memory']
                        cpu = input['cluster']['node'][i]['cpu']
                        label = input['cluster']['node'][i]['label']
                        creationTime = input['cluster']['wNode_creationTime']

                        node = Node(name, memory, cpu, cluster, label)  # create node
                        cluster.add_node(node)  # add node to the cluster
                        _NODES.append(node)

                        yield env.timeout(creationTime)

            except yaml.YAMLError as exc:
                print(exc)


def create_pods_yaml_generator(env, printing):
    '''
    This function creates all the pods described in the input (YAML) file.
    '''
    if printing:
        console.log("===> Creating Pods ", style="bold blue")

    pod_data = {}  # contains pod info described in the input file

    for filename in glob.glob('src/*.yaml'):
        with open(os.path.join(os.getcwd(), filename), 'r') as stream:
            try:
                input = yaml.safe_load(stream)
                for i in range(len(input['pods']['pod'])):
                    pod_name = input['pods']['pod'][i]['name']
                    plugin = input['pods']['pod'][i]['plugin']
                    arrivalRate = input['pods']['pod'][i]['arrivalRate']
                    serviceTime = input['pods']['pod'][i]['serviceTime']

                    pod_data[pod_name] = [plugin, arrivalRate, serviceTime]

            except yaml.YAMLError as exc:
                print(exc)

    container_list = []  # list of containers in the pod

    for filename in sorted(glob.glob('pods/*.yaml')):
        with open(os.path.join(os.getcwd(), filename), 'r') as stream:
            try:
                pod_file = yaml.safe_load(stream)
                name = pod_file['metadata']['name']

                if name in pod_data:
                    yield env.timeout(pod_data[name][1])
                    logging.info(' {} entered the queue at {} seconds \n'.format(
                                 name, env.now))
                    if printing:
                        console.log('---> {} entered the queue at {} seconds'.format(
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

                    pod = Pod(name, pod_memory, pod_cpu,
                              plug, env.now, pod_data[name][2],
                              container_list.copy(), nodeName,
                              nodeSelector, port, schedulerName)
                    _POD_QUEUE.put(pod)
                    _PODS.append(pod)
                    container_list.clear()

            except yaml.YAMLError as exc:
                print(exc)


def create_pods_csv_generator(env, jobs, printing):
    '''
    This function creates all the jobs described in the csv file.
    '''
    # seed random number generator
    seed(1)
    
    # extract data form the file
    df = pd.read_csv('src/jobs.csv')
    for i in range(jobs):
        yield env.timeout(random.exponential(scale=1.0, size=None))

        name = df['id'].values[i]
        duration = df['duration'].values[i]
        mem = df['mem'].values[i] * 64
        cpu = df['cpu'].values[i] * 128

        plug = Plugin()
        plugin_list = list(map(lambda x: x == "1", '0010000000001000001000'))
        plug.predicate_list = plugin_list[:9]
        plug.priorites_list = plugin_list[9:]

        logging.info(' {} entered the queue at {} seconds \n'.format(
                        name, env.now))
        if printing:
            console.log('---> {} entered the queue at {} seconds'.format(
                    name, env.now))

        pod = Pod(name, mem, cpu, plug, env.now, randint(duration, 200), [])
        _POD_QUEUE.put(pod)
        _PODS.append(pod)


def drop_pod_generator(env, pod, cluster, printing):
    '''
    This function removes the pod from the node it is bind to.
    '''
    if pod.is_bind:
        yield env.timeout(pod.serviceTime)

        if printing:
            console.log("\n===> Removing {} :hourglass: [{} seconds]".format(
                    pod.name, env.now), style="bold red")

        pod.node.remove_pod(pod)  # remove pod from the node
        # deactivating the node if it contains no pod
        if pod.node.num_of_pods == 0:
            pod.node.active = False
            cluster.active_nodes -= 1
        pod.node = None  # remove node from the pod

        logging.info(' {} removed at {} seconds\n'.format(pod.name, env.now))

    else:
        if printing:
            console.log("\n===> Can't Remove {} because it's not bind".format(
                    pod.name), style="bold red")
        logging.info(" Can't Remove {} because it's not bind\n".format(pod.name))

        if cluster.active_nodes > 0:
            if _POD_QUEUE.empty() is False:
                _POD_QUEUE.put(pod)
                pod.schedulingRetries += 1
                logging.info(' {} again entered the queue at {} seconds [Retry # {}]\n'.format(
                                    pod.name, env.now, pod.schedulingRetries))
                if printing:
                    console.log('---> {} again entered the queue at {} seconds [Retry # {}]'.format(
                                    pod.name, env.now, pod.schedulingRetries))
            else:
                logging.info(' No feasible node is available for {} in this cluster\n'.format(
                            pod.name))
                if printing:
                    console.log('---> No feasible node is available for {} in this cluster'.format(
                            pod.name))

        else:
            logging.info(' No feasible node is available for {} in this cluster\n'.format(
                         pod.name))
            if printing:
                console.log('---> No feasible node is available for {} in this cluster'.format(
                        pod.name))


def kubescheduler_generator(env, cluster, pod, printing):
    '''
    This function is used to schedule the pod on a feasible node.
    '''
    if printing:
        console.log("\n---> Run Kubescheduler for {}\n".format(
                pod.name), style="bold green")
    logging.info(" Run Kubescheduler for {}\n".format(
                pod.name))
    kubescheduler = Kubescheduler()  # create kubescheduler

    # Start kubescheduler
    kubescheduler.scheduling_cycle(cluster, pod, env.now, console, printing)

    index.append(env.now)
    pd_pods.append(pod.name)
    if pod.is_bind is True:
        logging.info(' {} assigned a node at {} seconds \n'.format(
                        pod.name, env.now))
        pd_status.append(True)
        pod.node.num_pod_history += 1
    else:
        pd_status.append(False)

    table.add_row(pod.name, str(pod.id), pod.assignedNode,
                  str(pod.memory), str(pod.cpu), str(pod.is_bind),
                  str(pod.port), str(pod.arrivalTime),
                  str(pod.serviceTime))

    # console.log(table)  # print table

    scheduling_time = 5  # time used by the scheduler to run its cycle
    yield env.timeout(scheduling_time)


# Utility function, returns average of a numerical list
def Average(lst):
    return reduce(lambda a, b: a + b, lst) / len(lst)


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
                wNodeList = input['cluster']['wNodeList']
                simType = input['metadata']['simType']
                jobType = input['metadata']['jobType']
                jobList = input['metadata']['csv']['jobList']
                num_yaml_pods = len(input['pods']['pod'])
                if input['metadata']['printing'] == 'on':
                    printing = True
                elif input['metadata']['printing'] == 'off':
                    printing = False

            except yaml.YAMLError as exc:
                print(exc)

    num_of_nodes = []
    num_of_jobs = []
    completion_time = []
    avg_wait_time = []
    avg_retries = []
    perc_failed_pods = []

    MARKDOWN = """# Start Simulation"""
    console.log(Markdown(MARKDOWN), style="bold magenta")

    total_nodes = list(map(int, wNodeList.split(",")))

    if jobType == 'yaml':
        jobList = [num_yaml_pods]
    elif jobType == 'csv':
        jobList = list(map(int, jobList.split(",")))

    for jobs in tqdm(jobList, desc="Working..."):
        for num_node in total_nodes:

            # create a simulation environment
            if simType == 'rt':
                env = simpy.rt.RealtimeEnvironment(factor=0.01, strict=False)
            elif simType == 'n':
                env = simpy.Environment()

            # erase logs of the previous run
            file = open("test.log", "r+")
            file.truncate(0)
            file.close()

            env.process(cluster_generator(env, num_mNode, num_node, jobs, jobType, printing))
            # Set the simulation to run till the cluster process finish
            env.run()

            total_completion_time = env.now
            logging.info(' Stop Cluster at {} seconds\n'.format(total_completion_time))
            if printing:
                console.log("\n---> Stop Cluster :hourglass: [{} seconds]\n".format(
                        total_completion_time), style="bold magenta")

            MARKDOWN = """# Experiment Done [Jobs: {}, Nodes: {}]""".format(jobs, num_node)
            console.log(Markdown(MARKDOWN), style="bold green")

            # for node in _NODES:
            #     node_table.add_row(node.name, str(node.id), str(node.num_of_pods),
            #                     str(node.memory), str(node.cpu), str(node.score),
            #                     str(node.port))
            # console.log(node_table)

            # table.add_row("---", "---", "---", "---",
            #               "---", "---", "---", "---", "---")

            # for pod in _PODS:
            #     table.add_row(pod.name, str(pod.id), pod.assignedNode,
            #                   str(pod.memory), str(pod.cpu), str(pod.is_bind),
            #                   str(pod.port), str(pod.arrivalTime),
            #                   str(pod.serviceTime))
            # console.log(table)

            # Creating DataFrame
            d = {
                "Pod": pd.Series(pd_pods, index),
                "Bind": pd.Series(pd_status, index)
            }
            df = pd.DataFrame(d)

            # sorting by first name
            df.sort_values("Pod", inplace = True)

            # dropping ALL duplicate values
            df.drop_duplicates(keep = 'last', subset ="Pod", inplace = True)

            retries = []
            wait_in_queue = []
            for pod in _PODS:
                retries.append(pod.schedulingRetries)
                wait_in_queue.append(pod.wait_in_queue)
            df['Retries'] = retries
            df['Wait in Queue'] = wait_in_queue

            if printing:
                console.log(df)  # displaying data

            if printing:
                console.log("\n---> Total Completion Time: {} seconds".format(
                        total_completion_time), style="bold green")
            logging.info(' Total Completion Time: {} seconds\n'.format(
                        total_completion_time))

            if printing:
                console.log("---> Average waiting time in the queue: {} seconds".format(
                        Average(wait_in_queue)), style="bold green")
            logging.info(' Average waiting time in the queue: {} seconds\n'.format(
                        Average(wait_in_queue)))

            if printing:
                console.log("---> Average retries: {}".format(
                        Average(retries)), style="bold green")
            logging.info(' Average retries: {}\n'.format(
                        Average(retries)))

            failed_pods = 0
            for pod in _PODS:
                if pod.binded is False:
                    failed_pods += 1

            if printing:
                console.log("---> Percentage of failed pods: {} %\n".format(
                        failed_pods/len(_PODS)), style="bold red")
            logging.info(' Percentage of failed pods: {} %\n'.format(
                        failed_pods/len(_PODS)))

            num_of_nodes.append(num_node)
            num_of_jobs.append(jobs)
            completion_time.append(total_completion_time)
            avg_wait_time.append(Average(wait_in_queue))
            avg_retries.append(Average(retries))
            perc_failed_pods.append(failed_pods/len(_PODS))

            _NODES.clear()
            _PODS.clear()
            index.clear()
            pd_pods.clear()
            pd_status.clear()

    data = {
             "num of nodes": num_of_nodes,
             "num of jobs": num_of_jobs,
             "completion time": completion_time,
             "avg waiting time in queue": avg_wait_time,
             "avg retries": avg_retries,
             "percentage of failed pods": perc_failed_pods
            }
    information = pd.DataFrame(data)

    information.to_csv('results.csv', index=False)
    console.save_html("demo.html")  # save the results in a demo HTML file

    MARKDOWN = """# End Simulation"""
    console.log(Markdown(MARKDOWN), style="bold magenta")

if __name__ == "__main__":
    main()
