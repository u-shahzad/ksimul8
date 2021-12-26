import random


class Predicates:
    '''
    Predicates are hard constraints that can't be violated. It is a
    combination of items provided by the system that users can apply
    '''
    def __init__(self) -> None:
        pass

    def podFitsHostPorts(self, node, pod):
        '''
            Checks if a Node has free ports (the network protocol kind)
            for the Pod ports the Pod is requesting.
        '''

        if pod.port in node.port:
            return False
        else:
            return True

    def podFitsHost(self, node, pod):
        '''
            Checks if a Pod specifies a specific Node by its hostname.
        '''

        if node.name == pod.nodeName:
            return True
        else:
            return False

    def podFitsResources(self, node, pod):
        '''
            Checks if the Node has free resources (eg, CPU and Memory)
            to meet the requirement of the Pod.
        '''

        if node.memory >= pod.memory and node.cpu >= pod.cpu:
            return True
        else:
            return False

    def matchNodeSelector(self, node, pod):
        '''
            Checks if a Pod's Node Selector matches the Node's label(s).
        '''

        if node.label is not None and node.label == pod.nodeSelector:
            return True
        else:
            return False

    def noVolumeZoneConflict(self, node, pod):
        '''
            Evaluate if the Volumes that a Pod requests are available on the
            Node, given the failure zone restrictions for that storage.
        '''

        return random.choice([True, False])

    def noDiskConflict(self, node, pod):
        '''
            Evaluates if a Pod can fit on a Node due to the volumes it
            requests, and those that are already mounted.
        '''

        return random.choice([True, False])

    def maxCSIVolumeCount(self, node, pod):
        '''
            Decides how many CSI volumes should be attached, and whether
            that's over a configured limit.
        '''

        return random.choice([True, False])

    def podToleratesNodeTaints(self, node, pod):
        '''
            checks if a Pod's tolerations can tolerate the Node's taints.
        '''

        return random.choice([True, False])

    def checkVolumeBinding(self, node, pod):
        '''
            Evaluates if a Pod can fit due to the volumes it requests.
            This applies for both bound and unbound PVCs.
            PV: https://kubernetes.io/docs/concepts/storage/persistent-volumes/
        '''

        return random.choice([True, False])
