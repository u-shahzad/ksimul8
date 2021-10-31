import simpy
import random
import json
import queue
from cluster import Cluster
from pod import Pod
from node import Node
from kubescheduler import Kubescheduler


def cluster_generator(env, inter_arrival_time, ideal_service_time):

    cluster = Cluster(env, 2)

    n1 = Node("n1", 1, 0, 4, 2.4)
    n2 = Node("n2", 2, 0, 2, 1.4)

    cluster.append(n1)
    cluster.append(n2)

    p1 = Pod("Pod1", 1, "Kubescheduler", "n1", "app", "nginx", 2, 1)
    p2 = Pod("Pod2", 2, "Kubescheduler", "n2", "app2", "redis", 1, 0.5)
    p3 = Pod("Pod3", 3, "Kubescheduler", "n2", "app3", "mongoDB", 4.2, 0.7)
    p4 = Pod("Pod4", 4, "Kubescheduler", "n1", "app4", "celery", 4.0, 0.7)

    pod_queue = queue.Queue()
    pod_queue.put(p1)
    pod_queue.put(p2)
    pod_queue.put(p3)

    # Keep doing this indefinitely (whilst the program's running)
    while True:

        # Tell the simulation enviroment to run the activity generator
        env.process(kubesched_generator(env, ideal_service_time, cluster, pod_queue.get()))

        # Calculate the time until the next pod arrives
        t = random.expovariate(1.0 / inter_arrival_time)

        # Tell the simulation to freeze this function in place
        # until that sampled inter-arrival time has elapsed
        yield env.timeout(t)


def kubesched_generator(env, ideal_service_time, cluster, pod):
    pod_arrival_time = env.now
    print("Pod ", pod.id, " entered queue at ", pod_arrival_time, sep="")

    kubescheduler = Kubescheduler("Kubescheduler")
    print("Pod Fits Host...")
    print(kubescheduler.podFitHost(cluster, pod))

    with cluster.num_of_nodes.request() as req:
        # The function freezes in place until the request can be met
        # (ie there is a node available for the request to be met).
        yield req
        # Once the function unfreezes, it'll resume from here, so when we get
        # to this point we know a node is now available. So we can record the
        # current simulation time, and therefore work out how long 
        # the pod was queuing.
        pod_assigned_node_time = env.now
        print("Pod ", pod.id, " assigned a node at ", pod_assigned_node_time, sep="")
        time_in_queue = (pod_assigned_node_time - pod_arrival_time)
        print("Pod ", pod.id, " queued for ", time_in_queue, " minutes.", sep="")

        # Now the pod is with the node, we need to calculate how long it will survive
        sampled_life_time = random.expovariate(1.0 / ideal_service_time)

        # Tell the simulation to freeze this function in place until that 
        # sampled life time has elapsed (which is also keeping the node in use
        # and unavailable elsewhere, as we are still in the 'with' statement)
        yield env.timeout(sampled_life_time)


def main():
    # We defined the generator functions above. Here's where we will get 
    # everything running. First we set up a new SimPy simulation enviroment
    env = simpy.Environment()

    inter_arrival_time = 5
    ideal_service_time = 6
    
    # Start up our Kube scheduler generator function so we start creating pods
    env.process(cluster_generator(env, inter_arrival_time, ideal_service_time))

    # Set the simulation to run for 30 time units (representing minutes in our
    # model, so for half hour of simulated time)
    env.run(until=30)


if __name__ == "__main__":
    main()

### Utility functions ###

def to_json(obj):
    return json.dumps(obj, default=lambda obj: obj.__dict__)