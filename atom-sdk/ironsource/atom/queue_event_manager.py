from event_manager import EventManager
from threading import Lock
from collections import deque
from event import Event


class QueueEventManager(EventManager):
    def __init__(self):
        """
        Queue event manager - store all data in queue
        """
        self._dictionary_lock = Lock()

        self._events = {}

    def add_event(self, event_object):
        """
        Add event object to queue

        :param event_object: event information object
        :type event_object: Event
        """
        with self._dictionary_lock:
            if not self._events.has_key(event_object.stream):
                self._events[event_object.stream] = deque()

            self._events[event_object.stream].append(event_object)

    def get_event(self, stream):
        """
        Get event object from queue

        :return Event information object from queue
        :rtype Event
        """
        with self._dictionary_lock:
            if self._events.has_key(stream) and (len(self._events[stream]) > 0):
                return self._events[stream].pop()

        return None
