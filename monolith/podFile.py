import yaml, glob, os
from pod import Pod


class PodFile:
    def __init__(self) -> None:
        pass

    def load(self, pod_queue):
        for filename in glob.glob('pods/*.yaml'):
            with open(os.path.join(os.getcwd(), filename), 'r') as stream:
                try:
                    # print (yaml.dump(yaml.safe_load(stream), default_flow_style=False))
                    pod_file = yaml.safe_load(stream)

                    pod = Pod(pod_file['metadata']['name'], 
                        pod_file['spec']['schedulerName'], 
                        pod_file['spec']['containers'][0]['name'], 
                        pod_file['spec']['containers'][0]['image'], 
                        int(pod_file['spec']['containers'][0]['resources']['limits']['memory'][:-2]), 
                        int(pod_file['spec']['containers'][0]['resources']['limits']['cpu'][:-1]))

                    pod_queue.put(pod)

                except yaml.YAMLError as exc:
                    print(exc)