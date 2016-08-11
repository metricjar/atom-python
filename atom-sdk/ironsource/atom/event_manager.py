import abc

from event import Event


class EventManager:
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        """
        Event manager interface for holding data
        """
        pass

    @abc.abstractmethod
    def add_event(self, event_object):
        """
        Add event (must to be synchronized)

        :param event_object: event data object
        :type event_object: Event
        """
        pass

    @abc.abstractmethod
    def get_event(self):
        """
        Get event (must to be synchronized)

        :return Event object from storage
        :rtype Event
        """
        pass
