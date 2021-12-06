from rich import style
from rich.console import Console
import time


console = Console()

class Priorites:

    '''
    Priorities are soft constraints. They may be violated, but it gives
    you an idea of how well the constraints are being met or not.
    '''

    def __init__(self):

        self.least_used_node = None
        self.most_used_node = None

    def selectorSpreadPriority():
        '''
        Spreads Pods across hosts, considering Pods that belong to
        the same Service, StatefulSet or ReplicaSet.
        '''

        pass

    def interPodAffinityPriority():
        '''
        Implements preferred inter pod affininity and antiaffinity.
        https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#inter-pod-affinity-and-anti-affinity
        '''

        pass

    def leastRequestedPriority(self, cluster):
        '''
        Favors nodes with fewer requested resources. In other words,
        the more Pods that are placed on a Node, and the more resources
        thosePods use, the lower the ranking this policy will give.
        '''

        nodes = cluster.getList()
        node_list = []

        for node in nodes:
            node_list.append(node.num_of_pods)

        node_list.sort()

        for node in nodes:
            if node.num_of_pods == node_list[0]:
                self.least_used_node = node
                break

        console.log(":arrow_lower_left:  Least used node {}".format(self.least_used_node.name),
                        style="cyan")
        time.sleep(0.1)
        self.least_used_node.score += 1

    def mostRequestedPriority(self, cluster):
        '''
        Favors nodes with most requested resources. This policy will fit
        the scheduled Pods onto the smallest number of Nodes needed to run
        your overall set of workloads.
        '''

        nodes = cluster.getList()
        node_list = []

        for node in nodes:
            node_list.append(node.num_of_pods)

        node_list.sort()

        for node in nodes:
            if node.num_of_pods == node_list[-1]:
                self.most_used_node = node
                break

        console.log(":arrow_upper_right:  Most used node {}".format(self.most_used_node.name),
                        style="cyan")
        time.sleep(0.1)
        self.most_used_node.score += 1

    def requestedToCapacityRatioPriority():
        '''
        Creates a requestedToCapacity based ResourceAllocationPriority
        using default resource scoring function shape.
        '''

        pass

    def balancedResourceAllocation():
        '''
        Favors nodes with balanced resource usage.
        '''

        pass

    def nodePreferAvoidPodsPriority():
        '''
        Prioritizes nodes according to the node annotation
        scheduler.alpha.kubernetes.io/preferAvoidPods. You can use this
        to hint that two different Pods shouldn't run on the same Node.
        '''

        pass

    def nodeAffinityPriority():
        '''
        Prioritizes nodes according to node affinity scheduling preferences
        indicated in PreferredDuringSchedulingIgnoredDuringExecution.
        You can read more about this in Assigning Pods to Nodes.
        '''

        pass

    def taintTolerationPriority():
        '''
        Prepares the priority list for all the nodes, based on the number of
        intolerable taints on the node. This policy adjusts a node's rank
        taking that list into account.
        '''

        pass

    def imageLocalityPriority(self, node, pod):
        '''
        Favors nodes that already have the container images for that
        Pod cached locally.
        '''

        for pod_list in node.pod_list:
            if pod_list.id == pod.id:
                pass
            elif pod_list.containerImage == pod.containerImage:
                return True
        return False

    def serviceSpreadingPriority():
        '''
        For a given Service, this policy aims to make sure that the Pods for
        the Service run on different nodes. It favours scheduling onto nodes
        that don't have Pods for the service already assigned there.
        The overall outcome is that the Service becomes more resilient to
        a single Node failure.
        '''

        pass

    def equalPriority():
        '''
        Gives an equal weight of one to all nodes.
        '''

        pass

    def evenPodsSpreadPriority():
        '''
        Implements preferred pod topology spread constraints.
        '''

        pass
