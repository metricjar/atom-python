from event_manager import EventManager
from threading import Lock
from collections import deque


class QueueEventManager(EventManager):
    """
        Queue event manager - store all data in queue
    """

    def __init__(self):
        self._dictionary_lock = Lock()

        self._events = {}

    def add_event(self, event_object):
        """
        Add event object to queue

        :param event_object: event information object
        :type event_object: Event
        """
        with self._dictionary_lock:
            if event_object.stream not in self._events:
                self._events[event_object.stream] = deque()

            self._events[event_object.stream].append(event_object)

    def get_event(self, stream):
        """
        Get event object from queue

        :return: Event information object from queue
        :rtype: Event
        """
        with self._dictionary_lock:
            if stream in self._events and (len(self._events[stream]) > 0):
                return self._events[stream].pop()

        return None
