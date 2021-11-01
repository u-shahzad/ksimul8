class Predicates:
    def __init__(self) -> None:
        pass

    def podFitsResources(self, cluster, pod):
        nodes = cluster.getList()
        for item in nodes:
            if item.memory >= pod.memory and item.cpu >= pod.cpu:
                return True
            else:
                return False