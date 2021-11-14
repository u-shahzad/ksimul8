class Priorites:
    def __init__(self) -> None:
        pass

    def imageLocalityPriority(self, node, pod):
        for pod_list in node.pod_list:
            if pod_list.id == pod.id:
                pass
            elif pod_list.containerImage == pod.containerImage:
                return True
        return False