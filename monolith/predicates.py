class Predicates:
    def __init__(self) -> None:
        pass

    def podFitHost(self, cluster, pod):
        nodes = cluster.getList()
        for item in nodes:
            if item.memory >= pod.memory:
                return True
            else:
                return False