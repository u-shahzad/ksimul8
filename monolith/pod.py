import itertools


class Pod:

    id_iter = itertools.count()

    def __init__(self, name, schedulerName, containerName,
                 containerImage, memory, cpu, plugins):

        self.name = name
        self.id = next(Pod.id_iter)
        self.schedulerName = schedulerName
        self.nodeName = ""
        self.containerName = containerName
        self.containerImage = containerImage
        self.memory = memory
        self.cpu = cpu
        self.is_bind = False
        self.plugins = plugins

    def serialize(self):

        return {"name": self.name,
                "podID": self.id,
                "schedulerName": self.schedulerName,
                "nodeName": self.nodeName,
                "containerName": self.containerName,
                "containerImage": self.containerImage,
                "memoryRequirement": self.memory,
                "cpuRequirement": self.cpu,
                "is_Bind": self.is_bind}

    def getID(self):

        return self.id
