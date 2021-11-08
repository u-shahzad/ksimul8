class Predicates:
    def __init__(self) -> None:
        pass

    def podFitsResources(self, cluster, pod):
        nodes = cluster.getList()
        for node in nodes:
            if node.memory >= pod.memory and node.cpu >= pod.cpu:
                return True
            else:
                return False