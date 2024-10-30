class BaseState(object):
    def __init__(self, **settings):
        self.__dict__.update(settings)
        self.done = False
        self.next = None
        self.quit = False
        self.previous = None
