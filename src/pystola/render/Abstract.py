from abc import ABCMeta, abstractmethod

class Abstract:

    def __init__(self):
        pass

    def set_verbosity_level(self, level):
        if level is None:
            level = 0
        self.level = level

    @abstractmethod
    def p(self, msg):
        pass

    @abstractmethod
    def d(self, msg):
        pass

    @abstractmethod
    def w(self, msg):
        pass

    @abstractmethod
    def e(self, msg):
        pass

    @abstractmethod
    def body(self, msg):
        pass

    @abstractmethod
    def header(self, header_dict):
        pass

    @abstractmethod
    def http_code(self, code):
        pass

