import simpy

class Cluster:
    def __init__(self, env, num_of_nodes):
        self.num_of_nodes = simpy.Resource(env, capacity = num_of_nodes)
        self.node_list = [] # list of nodes in cluster

    def append(self, elem):
        self.node_list.append(elem)
        
    def getList(self):
        return self.node_list