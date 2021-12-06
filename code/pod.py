import itertools


class Pod:

    '''
    A pod is the smallest execution unit in Kubernetes. A pod encapsulates
    one or more applications. Pods are ephemeral by nature, if a
    pod (or the node it executes on) fails, Kubernetes can automatically
    create a new replica of that pod to continue operations.
    '''

    id_iter = itertools.count()

    def __init__(self, name, schedulerName, containerName,
                 containerImage, memory, cpu, plugins, nodeName='',
                 nodeSelector='', port=None):

        self.name = name  # name of the pod
        self.id = next(Pod.id_iter)  # assigns unique id for each pod
        self.schedulerName = schedulerName  # name of scheduler that pod wants
        self.nodeName = nodeName  # name of node that the pod is bind to
        self.containerName = containerName  # name of container running in pod
        self.containerImage = containerImage  # image of the container
        self.memory = memory  # RAM requirements of the pod
        self.cpu = cpu  # CPU requirements of the pod
        self.is_bind = False  # initially pod is not bind
        self.plugins = plugins  # set of predicates and priorites for the pod
        self.nodeSelector = nodeSelector  # a field to check node label
        self.port = port  # network port requirement of the pod
        self.node = None  # the node object which pod will bind in the future

    def serialize(self):

        return {"name": self.name,
                "podID": self.id,
                "nodeName": self.nodeName,
                "containerImage": self.containerImage,
                "memoryRequirement": self.memory,
                "cpuRequirement": self.cpu,
                "is_Bind": self.is_bind,
                "Port": self.port}

    def getID(self):
        return self.id  # returns pod id
