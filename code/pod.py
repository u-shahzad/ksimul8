import itertools


class Pod:
    '''
    A pod is the smallest execution unit in Kubernetes. A pod encapsulates
    one or more applications. Pods are ephemeral by nature, if a
    pod (or the node it executes on) fails, Kubernetes can automatically
    create a new replica of that pod to continue operations.
    '''
    id_iter = itertools.count()

    def __init__(self, name, memory, cpu, plugin, arrivalTime,
                 serviceTime, containerList, nodeName='', nodeSelector='',
                 port=None, schedulerName='default-scheduler'):

        self.name = name  # name of the pod
        self.id = next(Pod.id_iter)  # assigns unique id for each pod
        self.schedulerName = schedulerName  # name of scheduler that pod wants
        self.nodeName = nodeName  # node that the pod prefers to bind
        self.memory = memory  # RAM requirements of the pod
        self.cpu = cpu  # CPU requirements of the pod
        self.is_bind = False  # initially pod is not bind
        self.plugin = plugin  # set of predicates and priorites for the pod
        self.nodeSelector = nodeSelector  # a field to check node label
        self.port = port  # network port requirement of the pod
        self.node = None  # the node object which pod will bind in the future
        self.arrivalTime = arrivalTime  # the time pod entered in the queue
        self.serviceTime = serviceTime  # time to live in the node
        self.container_list = containerList  # list of containers in the pod
        self.schedulingRetries = 0  # retries for scheduling an unassigned pod
        self.assignedNode = ''  # node name that the pod is bind to

    def serialize(self):
        return {"Name": self.name,
                "Pod ID": self.id,
                "nodeName": self.nodeName,
                "Memory Requirement": self.memory,
                "CPU Requirement": self.cpu,
                "is_bind": self.is_bind,
                "Port": self.port}
