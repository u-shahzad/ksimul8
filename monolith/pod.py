# from node import Node

class Pod:
    def __init__(self, name, id, schedulerName, nodeName, containerName, containerImage, memory, cpu):
        self.name = name
        self.id = id
        self.schedulerName = schedulerName
        self.nodeName = nodeName
        self.containerName = containerName
        self.containerImage = containerImage
        self.memory = memory
        self.cpu = cpu

    def serialize(self):
        return {"name": self.name,
                "podID": self.id,
                "schedulerName": self.schedulerName,
                "nodeName": self.nodeName,
                "containerName": self.containerName,
                "containerImage": self.containerImage,
                "memoryRequirement": self.memory,
                "cpuRequirement": self.cpu}

    def podName(self):
        return self.name