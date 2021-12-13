class Container:

    def __init__(self, name, image, memory, cpu):

        self.name = name  # name of the container
        self.image = image  # image of the container
        self.memory = memory  # memory requirement
        self.cpu = cpu  # cpu requirement
