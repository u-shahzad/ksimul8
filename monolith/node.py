from pod import Pod

class Node:
    def __init__(self, name, id, num_of_pods, memory, cpu):
        self.name = name
        self.id = id
        self.num_of_pods = num_of_pods
        self.memory = memory
        self.cpu = cpu
        self.pod_list = []
    
    def append(self, elem):
        self.pod_list.append(elem)
        self.num_of_pods += 1
        
    def getList(self):
        return self.pod_list