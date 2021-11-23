import simpy

class Cluster:
    def __init__(self, env):
        self.master_node = simpy.Resource(env, capacity = 1)
        self.node_list = [] # list of nodes in cluster

    def append(self, elem):
        self.node_list.append(elem)
        
    def getList(self):
        return self.node_list