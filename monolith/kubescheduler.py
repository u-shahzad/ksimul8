from predicates import Predicates
from priorites import Priorites


class Kubescheduler(Predicates, Priorites):
    def __init__(self, name):
        self.name = name
    
    def scheduling_cycle(self, cluster, pod):
        # apply predicates on node
        return self.podFitHost(cluster, pod)


        # apply priorites on node

