#!/usr/bin/env python

import simpy, random, json, queue, logging
from cluster import Cluster
import yaml, glob, os
from pod import Pod
from node import Node
from kubescheduler import Kubescheduler
from podFile import PodFile
from plugin import Plugin


logging.basicConfig(filename='test.log', level=logging.DEBUG,
                    format='%(asctime)s:%(levelname)s:%(message)s')


def create_nodes(cluster):

    for filename in glob.glob('src/*.yaml'):

            with open(os.path.join(os.getcwd(), filename), 'r') as stream:

                try:
                    input = yaml.safe_load(stream)

                    i = 0
                    while i < len(input['cluster']['node']):

                        name = input['cluster']['node'][i]['name']
                        memory = input['cluster']['node'][i]['memory']
                        cpu = input['cluster']['node'][i]['cpu']
                        label = input['cluster']['node'][i]['label']
                    
                        cluster.append(Node(name, memory, cpu, label))

                        i += 1

                except yaml.YAMLError as exc:

                    print(exc)


def create_pods():

    plug1 = Plugin(True, True, False, False, False, False, False, False, False
                , False, False, True, False, False, False, False, False, False
                , True, False, False, False)
    # plug1.customPlugin1()

    pod_queue = queue.Queue()

    for filename in glob.glob('src/*.yaml'):

            with open(os.path.join(os.getcwd(), filename), 'r') as stream:

                try:
                    input = yaml.safe_load(stream)

                    i = 0
                    while i < len(input['pods']['pod']):

                        name = input['pods']['pod'][i]['name']
                        schedulerName = input['pods']['pod'][i]['schedulerName']
                        containerName = input['pods']['pod'][i]['containerName']
                        containerImage = input['pods']['pod'][i]['containerImage']
                        plugin_check = input['pods']['pod'][i]['plugins']
                        nodeName = input['pods']['pod'][i]['nodeName']
                        nodeSelector = input['pods']['pod'][i]['nodeSelector']
                        memory = input['pods']['pod'][i]['memory']
                        cpu = input['pods']['pod'][i]['cpu']
                        port = input['pods']['pod'][i]['port']

                        plug = Plugin()

                        if plugin_check[0] == 'T':
                            plug._PodFitsHostPorts = True
                        if plugin_check[1] == 'T':
                            plug._PodFitsHost = True
                        if plugin_check[2] == 'T':
                            plug._PodFitsResources = True
                        if plugin_check[3] == 'T':
                            plug._MatchNodeSelector = True
                        if plugin_check[4] == 'T':
                            plug._NoVolumeZoneConflict = True
                        if plugin_check[5] == 'T':
                            plug._NoDiskConflict = True
                        if plugin_check[6] == 'T':
                            plug._MaxCSIVolumeCount = True
                        if plugin_check[7] == 'T':
                            plug._PodToleratesNodeTaints = True
                        if plugin_check[8] == 'T':
                            plug._CheckVolumeBinding = True
                        if plugin_check[9] == 'T':
                            plug._SelectorSpreadPriority = True
                        if plugin_check[10] == 'T':
                            plug._InterPodAffinityPriority = True
                        if plugin_check[11] == 'T':
                            plug._LeastRequestedPriority = True
                        if plugin_check[12] == 'T':
                            plug._MostRequestedPriority = True
                        if plugin_check[13] == 'T':
                            plug._RequestedToCapacityRatioPriority = True
                        if plugin_check[14] == 'T':
                            plug._BalancedResourceAllocation = True
                        if plugin_check[15] == 'T':
                            plug._NodePreferAvoidPodsPriority = True
                        if plugin_check[16] == 'T':
                            plug._NodeAffinityPriority = True
                        if plugin_check[17] == 'T':
                            plug._TaintTolerationPriority = True
                        if plugin_check[18] == 'T':
                            plug._ImageLocalityPriority = True
                        if plugin_check[19] == 'T':
                            plug._ServiceSpreadingPriority = True
                        if plugin_check[20] == 'T':
                            plug._EqualPriority = True
                        if plugin_check[21] == 'T':
                            plug._EvenPodsSpreadPriority = True                        
                    
                        pod_queue.put(Pod(name, schedulerName, containerName, 
                                        containerImage, memory, cpu, plug, nodeName, 
                                        nodeSelector, port))

                        i += 1

                except yaml.YAMLError as exc:

                    print(exc)
    
    pod_queue.put(Pod("Pod1", "default-scheduler", "appv2", "celery", 10, 16, plug, 'n4'))
    pod_queue.put(Pod("Pod2", "Kubescheduler", "appv1.1", "nginx", 2, 4, plug, 'n1'))
    pod_queue.put(Pod("Pod3", "Kubescheduler", "app", "celery", 20, 44, plug1, 'n4', '', 55))
    
    pod_file = PodFile()
    pod_file.load(pod_queue)

    return pod_queue


def cluster_generator(env, inter_arrival_time, ideal_service_time):

    cluster = Cluster(env)

    create_nodes(cluster)

    pod_queue = create_pods()

    # Keep doing this indefinitely (whilst the program's running)
    while True:

        if (pod_queue.empty() == False):
            # Tell the simulation enviroment to run the kubescheduler activity generator
            env.process(kubescheduler_generator(env, ideal_service_time, cluster, pod_queue.get()))

        # Calculate the time until the next pod arrives
        t = random.expovariate(1.0 / inter_arrival_time)

        # Tell the simulation to freeze this function in place
        # until that sampled inter-arrival time has elapsed
        yield env.timeout(t)


def kubescheduler_generator(env, ideal_service_time, cluster, pod):
    pod_arrival_time = env.now
    logging.info(' Pod {} entered queue at {} time unit \n'.format(pod.id, pod_arrival_time))

    with cluster.master_node.request() as req:
        # The function freezes in place until the request can be met
        # (ie there is a node available for the request to be met).

        yield req
        # Once the function unfreezes, it'll resume from here, so when we get
        # to this point we know a node is now available. So we can record the
        # current simulation time, and therefore work out how long 
        # the pod was queuing.

        kubescheduler = Kubescheduler("Kubescheduler")

        # Start kubescheduler
        kubescheduler.scheduling_cycle(cluster, pod)

        pod_assigned_node_time = env.now

        if pod.is_bind == True:
            logging.info(' Pod {} assigned a node at {} time unit \n'.format(pod.id, pod_assigned_node_time))
        print(pod.serialize(), '\n')
        
        scheduling_time = random.expovariate(1.0 / ideal_service_time)

        # Tell the simulation to freeze this function in place until that sampled
        # life time has elapsed (which is also keeping the master node in use
        # and unavailable elsewhere, as we are still in the 'with' statement)
        yield env.timeout(scheduling_time)


def main():
    # We defined the generator functions above. Here's where we will get 
    # everything running. First we set up a new SimPy simulation enviroment
    env = simpy.Environment()

    inter_arrival_time = 5
    ideal_service_time = 6
    
    # Start the cluster
    env.process(cluster_generator(env, inter_arrival_time, ideal_service_time))

    # Set the simulation to run for 60 time units (representing minutes in our
    # model, so for one hour of simulated time)
    env.run(until=60)


if __name__ == "__main__":
    main()

### Utility functions ###

def to_json(obj):
    return json.dumps(obj, default=lambda obj: obj.__dict__)