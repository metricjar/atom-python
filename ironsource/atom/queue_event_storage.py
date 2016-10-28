from ironsource.atom.event_storage import EventStorage
from threading import Lock
from collections import deque


class QueueEventStorage(EventStorage):
    """
        Queue event storage - in memory queue that implements ABC EventStorage
    """

    def __init__(self, queue_size):
        super(QueueEventStorage, self).__init__()
        self._dictionary_lock = Lock()
        self._queue_size = queue_size
        self._events = {}

    def add_event(self, event_object):
        """
        Add event object to queue

        :param event_object: Event object
        :type event_object: Event
        """
        with self._dictionary_lock:
            if event_object.stream not in self._events:
                self._events[event_object.stream] = deque(maxlen=self._queue_size)
            self._events[event_object.stream].append(event_object)

    def get_event(self, stream):
        """
        Get & remove event object from queue

        :return: Event object from queue
        :rtype: Event
        """
        with self._dictionary_lock:
            if stream in self._events and (len(self._events[stream]) > 0):
                return self._events[stream].popleft()

        return None

    def remove_event(self, stream):
        """
        Remove event object from queue

        :param stream: Atom stream name
        :type stream: str
        """
        with self._dictionary_lock:
            if stream in self._events and (len(self._events[stream]) > 0):
                return self._events[stream].popleft()

    def is_empty(self):
        """
        Check if the storage is empty

        :return: True is empty, else False
        """
        with self._dictionary_lock:
            for stream in self._events:
                if len(self._events[stream]) > 0:
                    return False
            return True
