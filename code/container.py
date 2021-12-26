class Container:
    '''
    Containers are a form of operating system virtualization. A single
    container might be used to run anything from a small microservice
    or software process to a larger application.
    '''
    def __init__(self, name, image, memory, cpu):
        self.name = name  # name of the container
        self.image = image  # image of the container
        self.memory = memory  # memory requirement
        self.cpu = cpu  # cpu requirement
