import abc

class Filter(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def apply(self, frame):
        pass

