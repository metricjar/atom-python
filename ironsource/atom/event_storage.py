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

        :param event_object: event data object
        :type event_object: Event
        """
        pass

    @abc.abstractmethod
    def get_event(self, stream):
        """
        Get event (must to be synchronized)

        :return: Event object from storage
        :rtype: Event
        """
        pass

    def remove_event(self, stream):
        """
        Remove event from storage
        :param stream:
        :return:
        """
