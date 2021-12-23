from pod import Pod
from plugin import Plugin
from container import Container
import yaml
import glob
import os


class CreatePod:

    def __init__(self):
        self.pod_list = []

    def create(self, pod_queue, pod_data):
        container_list = []

        for filename in glob.glob('pods/*.yaml'):
            with open(os.path.join(os.getcwd(), filename), 'r') as stream:
                try:
                    pod_file = yaml.safe_load(stream)

                    name = pod_file['metadata']['name']

                    if name in pod_data:

                        schedulerName = pod_file['spec']['schedulerName']
                        nodeName = pod_file['spec']['nodeName']
                        nodeSelector = pod_file['spec']['nodeSelector']['disktype']
                        port = pod_file['spec']['port']

                        for i in range(len(pod_file['spec']['containers'])):
                            containerName = pod_file['spec']['containers'][i]['name']
                            image = pod_file['spec']['containers'][i]['image']
                            memory = int(pod_file['spec']['containers'][i]['resources']['limits']['memory'][:-2])
                            cpu = int(pod_file['spec']['containers'][i]['resources']['limits']['cpu'][:-1])

                            container_list.append(Container(containerName,
                                                            image, memory,
                                                            cpu))

                        pod_memory = sum(map(lambda x: x.memory, container_list))
                        pod_cpu = sum(map(lambda x: x.cpu, container_list))

                        plug = Plugin()

                        plugin_list = list(map(lambda x: x == "1", pod_data[name][0]))

                        plug.predicate_list = plugin_list[:9]
                        plug.priorites_list = plugin_list[9:]

                        pod = Pod(name, schedulerName, pod_memory, pod_cpu,
                                  plug, pod_data[name][1], pod_data[name][2],
                                  container_list.copy(), nodeName,
                                  nodeSelector, port)
                        pod_queue.put(pod)
                        self.pod_list.append(pod)
                        container_list.clear()

                except yaml.YAMLError as exc:
                    print(exc)

        return self.pod_list
