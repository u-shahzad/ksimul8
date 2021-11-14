from predicates import Predicates
from priorites import Priorites


class Kubescheduler(Predicates, Priorites):
    def __init__(self, name):
        self.name = name
        self.predicates = False
        self.priorites = False
    
    def scheduling_cycle(self, cluster, pod):
        nodes = cluster.getList()

        # Predicates
        for node in nodes:

            if self.podFitsResources(node, pod) == True:
                node.append(pod)
                self.predicates = True
                break
        
        print('Predicates Status: ' + str(self.predicates))
        
        # Priorities
        for node in nodes:
            
            if self.imageLocalityPriority(node, pod) == True:
                self.priorites = True

        print('Priorites Status: ' + str(self.priorites))
