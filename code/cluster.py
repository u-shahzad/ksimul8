import simpy


class Cluster:

    def __init__(self, env, capacity):
        self.master_node = simpy.Resource(env, capacity=capacity)
        self.node_list = []  # list of nodes in cluster

    def append(self, elem):
        self.node_list.append(elem)  # insert a node in the cluster

    def getList(self):
        return self.node_list  # returns the list of nodes in the cluster
