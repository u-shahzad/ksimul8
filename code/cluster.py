import simpy


class Cluster:

    def __init__(self, env, capacity):
        self.master_node = simpy.Resource(env, capacity=capacity)
        self.node_list = []  # list of nodes in cluster

    def add_node(self, node):
        self.node_list.append(node)  # insert a node in the cluster

    def get_node_list(self):
        return self.node_list  # returns the list of nodes in the cluster
