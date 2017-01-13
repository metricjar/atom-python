import abc


class EventStorage:
    """
        Abstract Base Class for providing a generic way of storing events in a backlog before they are sent to Atom.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        pass

    @abc.abstractmethod
    def add_event(self, event_object):
        """
        Add event (must to be synchronized)

        :param event_object: Event data object
        :type event_object: Event
        """
        pass

    @abc.abstractmethod
    def get_event(self, stream):
        """
        Get event (must to be synchronized)

        :param stream: Atom stream name
        :type stream: str
        :return: Event object from storage
        :rtype: Event
        """
        pass

    @abc.abstractmethod
    def remove_event(self, stream):
        """
        Remove event from storage

        :param stream: Atom stream name
        :type stream str`
        """
        pass

    @abc.abstractmethod
    def is_empty(self):
        """
        Check if the storage is empty

        :return: True is empty, else False
        """
        pass
