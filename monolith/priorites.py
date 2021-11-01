class Priorites:
    def __init__(self) -> None:
        pass

    def imageLocalityPriority(self, cluster, pod):
        nodes = cluster.getList()
        for item in nodes:
            for pods in item.pod_list:
                if pods.containerImage == pod.containerImage:
                    return True
        return False