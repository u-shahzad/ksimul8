from predicates import Predicates
from priorites import Priorites


class Kubescheduler(Predicates, Priorites):
    def __init__(self, name):
        self.name = name
    
    def scheduling_cycle(self, cluster, pod):

        nodes = cluster.getList()

        for node in nodes:

            if pod.is_bind == False:
                self.apply_predicates(node, pod)
