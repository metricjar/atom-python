import abc


class EventManager:
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def add_event(self, event_object):
        pass

    @abc.abstractmethod
    def get_event(self):
        pass