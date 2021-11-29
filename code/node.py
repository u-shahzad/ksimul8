import itertools


class Node:
    id_iter = itertools.count()
    def __init__(self, name, memory, cpu, label = ''):
        self.name = name
        self.id = next(Node.id_iter)
        self.num_of_pods = 0 # initially node contains no pod
        self.memory = memory
        self.cpu = cpu
        self.score = 0
        self.port = []
        self.label = label
        self.pod_list = []
    
    def append(self, pod):
        self.pod_list.append(pod)
        self.memory -= pod.memory
        self.cpu -= pod.cpu
        pod.is_bind = True
        pod.nodeName = self.name
        self.num_of_pods += 1

        if pod.port is not None:
            self.port.append(pod.port)
        
    def getList(self):
        return self.pod_list

    def serialize(self):
        return {"name": self.name,
                "ID": self.id,
                "Num of Pods": self.num_of_pods,
                "Memory": self.memory,
                "CPU": self.cpu,
                "Score": self.score,
                "Port": self.port}