from typing import Container
import yaml, glob, os
from pod import Pod
from plugin import Plugin
from container import Container


class PodFile:

    def __init__(self) -> None:
        pass

    def load(self, pod_queue, pod_name, plugin, arrivalTime, serviceTime):
        file = 0
        container_list = []

        for filename in glob.glob('pods/*.yaml'):
            with open(os.path.join(os.getcwd(), filename), 'r') as stream:
                try:
                    # print (yaml.dump(yaml.safe_load(stream), default_flow_style=False))
                    pod_file = yaml.safe_load(stream)

                    name = pod_file['metadata']['name']

                    if name in pod_name:

                        plug = Plugin(
                                False, False, True, False, False, False, False, False, False,
                                False, False, True, False, False, False, False, False,
                                False, True, False, False, False
                                )

                        schedulerName = pod_file['spec']['schedulerName']
                        nodeName = pod_file['spec']['nodeName']
                        nodeSelector = pod_file['spec']['nodeSelector']['disktype']
                        port = pod_file['spec']['port']

                        for i in range(len(pod_file['spec']['containers'])):
                            containerName = pod_file['spec']['containers'][i]['name']
                            image = pod_file['spec']['containers'][i]['image']
                            memory = int(pod_file['spec']['containers'][i]['resources']['limits']['memory'][:-2])
                            cpu = int(pod_file['spec']['containers'][i]['resources']['limits']['cpu'][:-1])

                            container_list.append(Container(containerName, image,
                                                    memory, cpu))

                        pod_memory = sum(map(lambda x: x.memory, container_list))
                        pod_cpu = sum(map(lambda x: x.cpu, container_list))

                        pod_queue.put(Pod(name, schedulerName, pod_memory, pod_cpu, plug,
                                    arrivalTime[file], serviceTime[file], container_list,
                                    nodeName, nodeSelector, port))
                    file += 1

                except yaml.YAMLError as exc:
                    print(exc)