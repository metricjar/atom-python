from threading import Thread
from collections import deque


class BatchEventPoolException(Exception):
    """
    Event task pool exception
    """
    pass


class BatchEventPool:
    """
        Batch Event Pool constructor

        :param thread_count: count of working threads
        :type thread_count: int
        :param max_events: max count of events in queue
        :type max_events: int
    """

    def __init__(self, thread_count, max_events):
        self._events = deque(maxlen=max_events)

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
        self._is_running = False

    def task_worker(self):
        """
        Worker method - for call action lambda
        """
        while self._is_running:
            if len(self._events) > 0:
                try:
                    action = self._events.popleft()
                except IndexError:
                    continue

                action()

    def add_event(self, event_action):
        """
        Add event for task pool

        :param event_action: event lambda
        :type event_action: lambda
        :raises: EventTaskPoolException
        """
        if (len(self._events) + 1) > self._max_events:
            raise BatchEventPoolException("Exceeded max event count in Event Task Pool!")

        self._events.append(event_action)

    def is_empty(self):
        return not self._events
