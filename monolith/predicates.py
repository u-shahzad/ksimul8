class Predicates:

    def __init__(self) -> None:

        pass

    def apply_predicates(self, node, pod):

        while(True):

            if pod.plugins._PodFitsResources:
                if node.memory >= pod.memory and node.cpu >= pod.cpu:
                    pass
                else:
                    break

            if pod.plugins._PodFitsHostPorts:
                if node.port == True:
                    pass
                else:
                    break

            node.append(pod)
            break

    def podFitsHostPorts(self, node):
        '''
            Checks if a Node has free ports (the network protocol kind)
            for the Pod ports the Pod is requesting.
        '''

        if node.port == True:
            return True
        else:
            return False

    def podFitsHost():
        '''
            Checks if a Pod specifies a specific Node by its hostname.
        '''

        pass

    def podFitsResources(self, node, pod):
        '''
            Checks if the Node has free resources (eg, CPU and Memory)
            to meet the requirement of the Pod.
        '''

        if node.memory >= pod.memory and node.cpu >= pod.cpu:
            return True
        else:
            return False

    def matchNodeSelector():
        '''
            Checks if a Pod's Node Selector matches the Node's label(s).
        '''

        pass

    def noVolumeZoneConflict():
        '''
            Evaluate if the Volumes that a Pod requests are available on the
            Node, given the failure zone restrictions for that storage.
        '''

        pass

    def noDiskConflict():
        '''
            Evaluates if a Pod can fit on a Node due to the volumes it
            requests, and those that are already mounted.
        '''

        pass

    def maxCSIVolumeCount():
        '''
            Decides how many CSI volumes should be attached, and whether
            that's over a configured limit.
        '''

        pass

    def podToleratesNodeTaints():
        '''
            checks if a Pod's tolerations can tolerate the Node's taints.
        '''

        pass

    def checkVolumeBinding():
        '''
            Evaluates if a Pod can fit due to the volumes it requests.
            This applies for both bound and unbound PVCs.
            PV: https://kubernetes.io/docs/concepts/storage/persistent-volumes/
        '''

        pass
