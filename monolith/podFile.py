import yaml, glob, os
from pod import Pod
from plugin import Plugin


class PodFile:

    def __init__(self) -> None:
        pass

    def load(self, pod_queue):
        for filename in glob.glob('pods/*.yaml'):
            with open(os.path.join(os.getcwd(), filename), 'r') as stream:
                try:
                    # print (yaml.dump(yaml.safe_load(stream), default_flow_style=False))
                    pod_file = yaml.safe_load(stream)

                    plug = Plugin()
                    plug.customPlugin2()

                    name = pod_file['metadata']['name']
                    schedulerName = pod_file['spec']['schedulerName']
                    containerName = pod_file['spec']['containers'][0]['name']
                    image = pod_file['spec']['containers'][0]['image']
                    memory = int(pod_file['spec']['containers'][0]['resources']['limits']['memory'][:-2])
                    cpu = int(pod_file['spec']['containers'][0]['resources']['limits']['cpu'][:-1])
                    nodeName = pod_file['spec']['nodeName']

                    pod = Pod(name, schedulerName, containerName, image, memory, cpu, plug, nodeName)

                    pod_queue.put(pod)

                except yaml.YAMLError as exc:
                    print(exc)