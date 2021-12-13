from typing import Container
import yaml, glob, os
from pod import Pod
from plugin import Plugin
from container import Container
import numpy as np


class CreatePod:

    def __init__(self):
        self.pod_list = []

    def create(self, pod_queue, pod_name, plugin, arrivalRate, serviceTime):
        file = 0
        container_list = []

        for filename in glob.glob('pods/*.yaml'):
            with open(os.path.join(os.getcwd(), filename), 'r') as stream:
                try:
                    # print (yaml.dump(yaml.safe_load(stream), default_flow_style=False))
                    pod_file = yaml.safe_load(stream)

                    name = pod_file['metadata']['name']

                    if name in pod_name:

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

                        plug = Plugin()

                        plugin_list = self.num_to_list(plugin[file])
                        plug.predicate_list = plugin_list[:9]
                        plug.priorites_list = plugin_list[9:]

                        pod = Pod(name, schedulerName, pod_memory, pod_cpu,
                                plug, arrivalRate[file], serviceTime[file],
                                container_list, nodeName, nodeSelector, port)
                        pod_queue.put(pod)
                        self.pod_list.append(pod)
                        container_list.clear()

                    file += 1

                except yaml.YAMLError as exc:
                    print(exc)

        return self.pod_list

    def num_to_list(self, num):

        res = [int(x) for x in str(num)]  # create list of num (0's and 1's)
        res_array = np.array(res)  # convert list to numpy array
        bool_array = res_array>0  # convert array to boolean array
        bool_list = bool_array.tolist()  # convert boolean array to list
        del bool_list[0]  # delete first bit

        return bool_list