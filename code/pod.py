import itertools


class Pod:

    '''
    A pod is the smallest execution unit in Kubernetes. A pod encapsulates
    one or more applications. Pods are ephemeral by nature, if a
    pod (or the node it executes on) fails, Kubernetes can automatically
    create a new replica of that pod to continue operations.
    '''

    id_iter = itertools.count()

    def __init__(self, name, schedulerName, memory, cpu, plugin, arrivalTime,
                 serviceTime, containerList, nodeName='', nodeSelector='',
                 port=None):

        self.name = name  # name of the pod
        self.id = next(Pod.id_iter)  # assigns unique id for each pod
        self.schedulerName = schedulerName  # name of scheduler that pod wants
        self.nodeName = nodeName  # name of node that the pod is bind to
        self.memory = memory  # RAM requirements of the pod
        self.cpu = cpu  # CPU requirements of the pod
        self.is_bind = False  # initially pod is not bind
        self.plugin = plugin  # set of predicates and priorites for the pod
        self.nodeSelector = nodeSelector  # a field to check node label
        self.port = port  # network port requirement of the pod
        self.node = None  # the node object which pod will bind in the future
        self.arrivalTime = arrivalTime
        self.serviceTime = serviceTime
        self.container_list = containerList  # list of containers in the pod

    def serialize(self):

        return {"Name": self.name,
                "Pod ID": self.id,
                "nodeName": self.nodeName,
                "Memory Requirement": self.memory,
                "CPU Requirement": self.cpu,
                "is_bind": self.is_bind,
                "Port": self.port}
