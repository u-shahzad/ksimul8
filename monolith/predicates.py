class Predicates:
    def __init__(self) -> None:
        pass

    def podFitsResources(self, node, pod):
        if node.memory >= pod.memory and node.cpu >= pod.cpu:
            return True
        else:
            return False