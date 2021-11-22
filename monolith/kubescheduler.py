from predicates import Predicates
from priorites import Priorites
from node import Node
import random


class Kubescheduler(Predicates, Priorites):

    def __init__(self, name):

        self.name = name
        self.feasible_nodes = []
        self.selected_node = None
    
    def scheduling_cycle(self, cluster, pod):

        nodes = cluster.getList()
        node_rank = 0

        for node in nodes:

            while (True):

                # Applying Predicates

                if pod.plugins._PodFitsResources:
                    if (self.podFitsResources(node, pod)):
                        pass
                    else:
                        break

                if pod.plugins._PodFitsHostPorts:
                    if (self.podFitsHostPorts(node)):
                        pass
                    else:
                        break

                if pod.plugins._PodFitsHost:
                    if (self.podFitsHost(node, pod)):
                        pass
                    else:
                        break

                self.feasible_nodes.append(node)
                break

            # Applying Priorites

            if pod.plugins._ImageLocalityPriority:
                if (self.imageLocalityPriority(node, pod)):
                    node.score += 1

        # 

        if len(self.feasible_nodes) > 0:

            # If multiple feasible nodes found, select on the basis of node score

            for feasible_node in self.feasible_nodes:
                print(feasible_node.name)
                if feasible_node.score > node_rank:
                    node_rank = feasible_node.score
                    self.selected_node = feasible_node

            if self.selected_node is None:
                self.selected_node = random.choice(self.feasible_nodes)

            print('Selected node: '+ self.selected_node.name)
            self.selected_node.append(pod)
