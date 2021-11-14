from pod import Pod

class Node:
    def __init__(self, name, id, memory, cpu):
        self.name = name
        self.id = id
        self.num_of_pods = 0 # initially node contains no pod
        self.memory = memory
        self.cpu = cpu
        self.pod_list = []
    
    def append(self, pod):
        self.pod_list.append(pod)
        self.memory -= pod.memory
        pod.is_bind = True
        pod.nodeName = self.name
        self.num_of_pods += 1
        
    def getList(self):
        return self.pod_list

    def serialize(self):
        return {"name": self.name,
                "ID": self.id,
                "Num of Pods": self.num_of_pods,
                "Memory": self.memory,
                "CPU": self.cpu,
                "Pod List": self.pod_list}