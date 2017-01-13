from ironsource.atom.event_storage import EventStorage
from Queue import Queue
from threading import Lock


class QueueEventStorage(EventStorage):
    """
        Queue event storage - in memory queue that implements ABC EventStorage
    """

    def __init__(self, queue_size, block=True, timeout=None):
        """
        :param queue_size: Queue size
        :param block: Should the put to Queue block or not
        :param timeout: Timeout in case we are blocking
        """
        super(QueueEventStorage, self).__init__()
        self._dictionary_lock = Lock()
        self._queue_size = queue_size
        self._events = {}
        self._block = block
        self._timeout = timeout if not block else None

        print("timeout: {}, block: {}".format(self._timeout, self._block))

    def add_event(self, event_object):
        """
        Add event object to queue

        :param event_object: Event object
        :type event_object: Event
        """
        with self._dictionary_lock:
            if event_object.stream not in self._events:
                self._events[event_object.stream] = Queue(maxsize=self._queue_size)
            self._events[event_object.stream].put(event_object, block=self._block, timeout=self._timeout)

    def get_event(self, stream):
        """
        Get & remove event object from queue

        :type stream: Atom stream name
        :return: Event object from queue
        :rtype: Event
        """
        if stream in self._events and not self._events[stream].empty():
            return self._events[stream].get(block=self._block, timeout=self._timeout)

    def remove_event(self, stream):
        """
        Remove event object from queue

        :param stream: Atom stream name
        :type stream: str
        """
        return self.get_event(stream)

    def is_empty(self):
        """
        Check if the storage is empty

        :return: True is empty, else False
        """
        for stream in self._events:
            if not self._events[stream].empty():
                return False
        return True
