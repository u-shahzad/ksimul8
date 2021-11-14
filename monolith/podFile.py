import yaml, glob, os


class PodFile:
    def __init__(self) -> None:
        pass

    def load(self):
        for filename in glob.glob('pods/*.yaml'):
            with open(os.path.join(os.getcwd(), filename), 'r') as stream:
                try:
                    print (yaml.dump(yaml.safe_load(stream), default_flow_style=False))
                    # print(yaml.safe_load(stream))
                except yaml.YAMLError as exc:
                    print(exc)