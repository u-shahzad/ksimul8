import itertools


class Node:

    '''
    A Node is a worker machine in Kubernetes and may be either a virtual or a
    physical machine, depending on the cluster. Each Node is managed by the
    control plane. A Node can have multiple pods, and the Kubernetes control
    plane automatically handles scheduling the pods across the Nodes in the
    cluster.
    '''

    id_iter = itertools.count()

    def __init__(self, name, memory, cpu, label=''):
        self.name = name  # name of the node
        self.id = next(Node.id_iter)  # select unique id for each node
        self.num_of_pods = 0  # initially node contains no pod
        self.memory = memory  # RAM resource of the node
        self.cpu = cpu  # CPU resource of the node
        self.score = 0  # the rank of the node (used in scheduling)
        self.port = []  # list of network ports
        self.label = label  # defines some extra feature in the node
        self.pod_list = []  # contains list of running pods in the node

    def append(self, pod):
        self.pod_list.append(pod)  # bind pod to the node
        self.memory -= pod.memory  # decreasing node memory resource
        self.cpu -= pod.cpu  # decreasing node cpu resource
        pod.is_bind = True  # changing pod state to bind
        pod.nodeName = self.name  # changing node name of the pod
        self.num_of_pods += 1  # increment the number of pods in the node

        # if pod also contains a network port, add in the port list
        if pod.port is not None:
            self.port.append(pod.port)

    def getList(self):
        return self.pod_list  # returns the list of pods in the node

    def serialize(self):
        return {"name": self.name,
                "ID": self.id,
                "Num of Pods": self.num_of_pods,
                "Memory": self.memory,
                "CPU": self.cpu,
                "Score": self.score,
                "Port": self.port}
