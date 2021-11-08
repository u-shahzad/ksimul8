class Priorites:
    def __init__(self) -> None:
        pass

    def imageLocalityPriority(self, cluster, pod):
        nodes = cluster.getList()
        for node in nodes:
            for pod_list in node.pod_list:
                if pod_list.containerImage == pod.containerImage:
                    return True
        return False