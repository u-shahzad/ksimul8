from predicates import Predicates
from priorites import Priorites


class Kubescheduler(Predicates, Priorites):
    def __init__(self, name):
        self.name = name
    
    def scheduling_cycle(self, cluster, pod):
        
        # Apply Predicates

        # Apply Priorities
        
        return ""
