from threading import Thread
from Queue import Queue


class BatchEventPool:
    """
        Batch Event Pool constructor

        :param thread_count: Count of working threads
        :type thread_count: int
        :param max_events: Max count of events in queue
        :type max_events: int
    """

    def __init__(self, thread_count, max_events):
        self._events = Queue(maxsize=max_events)

        self._is_running = True
        self._max_events = max_events

        self._workers = []

        for index in range(0, thread_count):
            thread = Thread(target=self.task_worker)
            self._workers.append(thread)
            thread.start()

    def stop(self):
        """
        Stop all working threads
        """
        # The put event is here to unblock the task_worker (get() is blocking)
        self._events.put(lambda: 0)
        self._is_running = False

    def task_worker(self):
        """
        Worker method - for call action lambda
        """
        while self._is_running:
            func = self._events.get()
            func()

    def add_event(self, event_action):
        """
        Add event for task pool

        :param timeout: timeout in seconds (Raises Full exception after x seconds)
        :type timeout: int
        :param block: put an item if one is available, else raise Full exception (timeout is ignored in that case).
        :type block: bool
        :param event_action: event lambda
        :type event_action: lambda
        :raises: EventTaskPoolException
        """
        self._events.put(event_action)

    def is_empty(self):
        """
        Check if the event pool is empty
        :return: True if empty, else False
        """
        return self._events.empty()
