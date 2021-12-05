from predicates import Predicates
from priorites import Priorites
import logging


logging.basicConfig(filename='test.log', level=logging.DEBUG,
                    format='%(asctime)s:%(levelname)s:%(message)s')


class Kubescheduler(Predicates, Priorites):

    '''
    The Kubernetes scheduler is a control plane process which assigns Pods to
    Nodes. The scheduler determines which Nodes are valid placements for each
    Pod in the scheduling queue according to constraints and available
    resources. The scheduler then ranks each valid Node and binds the Pod to
    a suitable Node.
    '''

    def __init__(self, name='Kubescheduler'):
        self.name = name  # name of the scheduler
        self.feasible_nodes = []  # list of feasible nodes for the pod
        self.selected_node = None  # final selected node for the pod

    def node_score(self, node):
        return node.score  # returns the score of the node

    def scheduling_cycle(self, cluster, pod):
        nodes = cluster.getList()  # list of all the nodes
        lrp_check = False  # check for LeastRequestedPriority
        mrp_check = False  # check for MostRequestedPriority

        for node in nodes:

            '''
            This loop will only execute a single iteration and finds
            the number of feasible node(s) for the pod by applying a
            set of predicates.
            '''
            while (True):

                # Applying Predicates

                if pod.plugins._PodFitsResources:
                    if (self.podFitsResources(node, pod)):
                        pass
                    else:
                        break

                if pod.plugins._PodFitsHostPorts:
                    if (self.podFitsHostPorts(node, pod)):
                        pass
                    else:
                        break

                if pod.plugins._PodFitsHost:
                    if (self.podFitsHost(node, pod)):
                        pass
                    else:
                        break

                if pod.plugins._MatchNodeSelector:
                    if (self.matchNodeSelector(node, pod)):
                        pass
                    else:
                        break

                self.feasible_nodes.append(node)
                break

            # Applying Priorites

            if pod.plugins._ImageLocalityPriority:
                if (self.imageLocalityPriority(node, pod)):
                    node.score += 1

            if pod.plugins._LeastRequestedPriority and lrp_check is False:
                self.leastRequestedPriority(cluster)
                lrp_check = True

            if pod.plugins._MostRequestedPriority and mrp_check is False:
                self.mostRequestedPriority(cluster)
                mrp_check = True

        # check that feasible nodes list is not empty
        if len(self.feasible_nodes) > 0:

            # sort the nodes on the basis of their score
            self.feasible_nodes.sort(key=self.node_score)

            # select the node with the highest score
            self.selected_node = self.feasible_nodes[-1]
            self.selected_node.append(pod)  # add the pod to the selected node

            logging.info(' \"Selected Node: {}\"\n'.format(
                            self.selected_node.name))

        for node in nodes:
            print(node.serialize(), '\n')
            node.score = 0  # clear the node score for the next pod scheduling
