import simpy


class Cluster:
    '''
    A Kubernetes cluster is a set of nodes that run containerized applications
    '''
    def __init__(self, env, capacity, status=False):
        self.master_node = simpy.Resource(env, capacity=capacity)
        self.node_list = []  # list of nodes in cluster
        self.active_nodes = 0  # initially no nodes are active

    def add_node(self, node):
        self.node_list.append(node)  # insert a node in the cluster

    def get_node_list(self):
        return self.node_list  # returns the list of nodes in the cluster
