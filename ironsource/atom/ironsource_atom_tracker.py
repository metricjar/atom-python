import json
import signal

from ironsource.atom.ironsource_atom import IronSourceAtom
from ironsource.atom.queue_event_storage import QueueEventStorage
from ironsource.atom.batch_event_pool import BatchEventPool
from ironsource.atom.event import Event

import sys
import time
import math
import random
import logging

from threading import Lock
from threading import Thread


class IronSourceAtomTracker:
    """
       ironSource Atom high level API class (Tracker), supports: track() and flush()
    """
    _TAG = "IronSourceAtomTracker"

    _BULK_SIZE = 500
    _BULK_BYTES_SIZE = 64 * 1024

    _FLUSH_INTERVAL = 10000

    # Default Number of workers(threads) for BatchEventPool
    _BATCH_WORKER_COUNT = 1
    # Default Number of events to hold in BatchEventPool
    _BATCH_POOL_SIZE = 3000
    # Default backlog queue size (per stream)
    _BACKLOG_SIZE = 12000
    # Retry on 500 / Connection error conf
    _RETRY_MIN_TIME = 1
    _RETRY_MAX_TIME = 10

    def __init__(self, batch_worker_count=_BATCH_WORKER_COUNT, batch_pool_size=_BATCH_POOL_SIZE,
                 backlog_size=_BACKLOG_SIZE):

        self._api = IronSourceAtom()
        self._is_debug = False
        self._is_run_worker = True
        self._is_flush_data = False

        # calculate current milliseconds
        self._current_milliseconds = lambda: int(round(time.time() * 1000))

        self._data_lock = Lock()

        # Streams to keys map
        self._stream_keys = {}

        self._retry_min_time = IronSourceAtomTracker._RETRY_MIN_TIME
        self._retry_max_time = IronSourceAtomTracker._RETRY_MAX_TIME

        self._bulk_size = IronSourceAtomTracker._BULK_SIZE
        self._bulk_bytes_size = IronSourceAtomTracker._BULK_BYTES_SIZE

        self._flush_interval = IronSourceAtomTracker._FLUSH_INTERVAL

        # Holds the events after .track method
        self._event_backlog = QueueEventStorage(queue_size=backlog_size)

        # Holds batch of events for each stream and sends them using {thread_count} workers
        self._batch_event_pool = BatchEventPool(thread_count=batch_worker_count,
                                                max_events=batch_pool_size)

        handler_thread = Thread(target=self._tracker_handler)
        handler_thread.start()

        # init default logger
        self._logger = logging.getLogger("ATOM-TRACKER")
        self._logger.setLevel(logging.DEBUG)

        stream_object = logging.StreamHandler(sys.stdout)
        stream_object.setLevel(logging.DEBUG)
        logger_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        stream_object.setFormatter(logger_formatter)
        self._logger.addHandler(stream_object)

        # Intercept exit signals
        signal.signal(signal.SIGTERM, self.graceful_kill)
        signal.signal(signal.SIGINT, self.graceful_kill)

    def stop(self):
        """
        Stop worker thread and event_pool thread's
        """
        # flush everything todo: add flush_all method
        self.print_log("Flushing all data and killing the tracker")
        self._is_run_worker = False
        self._batch_event_pool.stop()

    def set_logger(self, logger):
        """
        Set custom logger

        :param logger: custom logger object
        :type logger: logging.Logger
        """
        self._logger = logger
        self._api.set_logger(logger)

    def set_event_manager(self, event_manager):
        """
        Set custom event manager object

        :param event_manager: custom event manager for storage data
        :type event_manager: EventManager
        """
        self._event_backlog = event_manager

    def enable_debug(self, is_debug):
        """
        Enable print information

        :param is_debug: enable print debug info
        :type is_debug: bool
        """
        self._is_debug = is_debug

    def set_endpoint(self, endpoint):
        """
        Set server host address

        :param endpoint: server url
        :type endpoint: str
        """
        self._api.set_endpoint(endpoint)

    def set_auth(self, auth_key):
        """
        Set auth key for stream

        :param auth_key: secret auth key
        :type auth_key: str
        """
        self._api.set_auth(auth_key)

    def set_bulk_size(self, bulk_size):
        """
        Set bulk count

        :param bulk_size: count of bulk events
        :type bulk_size: int
        """
        self._bulk_size = bulk_size

    def set_bulk_bytes_size(self, bulk_bytes_size):
        """
        Set bulk bytes size

        :param bulk_bytes_size: bulk size in bytes
        :type bulk_bytes_size: int
        """
        self._bulk_bytes_size = bulk_bytes_size

    def set_flush_interval(self, flush_interval):
        """
        Set flush interval milliseconds

        :param flush_interval: interval for flush data
        :type flush_interval: int
        """
        self._flush_interval = flush_interval

    def track(self, stream, data, auth_key=""):
        """
        Track event

        :param stream: name of stream
        :type stream: str
        :param data: data for sending
        :type data: object
        :param auth_key: secret auth key for stream
        :type auth_key: str
        """
        if len(auth_key) == 0:
            auth_key = self._api.get_auth()

        if not isinstance(data, str):
            data = json.dumps(data)

        with self._data_lock:
            if stream not in self._stream_keys:
                self._stream_keys[stream] = auth_key

            self._event_backlog.add_event(Event(stream, data))

    def flush(self):
        """
        Flush data from all streams
        """
        self._is_flush_data = True

    def _tracker_handler(self):
        """
        Main tracker function, handles flushing
        """
        # Temp buffer between backlog and batch pool
        events_buffer = {}
        # Dict to hold events size for every stream
        events_size = {}

        def flush_data(stream, auth_key):
            inner_buffer = list(events_buffer[stream])
            del events_buffer[stream][:]
            events_size[stream] = 0
            self._batch_event_pool.add_event(lambda: self._flush_data(stream, auth_key, inner_buffer))

        while self._is_run_worker:
            for stream_name, stream_value in self._stream_keys.items():

                # if stream_name in events_buffer and len(events_buffer[stream_name]) > 0:
                # flush_data(stream_name, auth_key=self._stream_keys[stream_name])

                # todo: fix time interval

                # Get one event from the backlog
                event_object = self._event_backlog.get_event(stream_name)
                if event_object is None:
                    continue

                if stream_name not in events_size:
                    events_size[stream_name] = 0

                if stream_name not in events_buffer:
                    events_buffer[stream_name] = []

                events_size[stream_name] += len(event_object.data.encode("utf8"))
                events_buffer[stream_name].append(event_object.data)

                if events_size[stream_name] >= self._bulk_bytes_size:
                    flush_data(stream_name, auth_key=self._stream_keys[stream_name])

                if len(events_buffer[stream_name]) > self._bulk_size:
                    flush_data(stream_name, auth_key=self._stream_keys[stream_name])

                if self._is_flush_data:
                    flush_data(stream_name, auth_key=self._stream_keys[stream_name])

            if self._is_flush_data:
                self._is_flush_data = False

    def _flush_data(self, stream, auth_key, data):
        """
        Send data to server through IronSource Atom Low-level API
        """
        attempt = 1

        while self._is_run_worker:
            response = self._api.put_events(stream, data=data, auth_key=auth_key)
            if 500 > response.status > 1:
                self.print_log("Sent: " + str(data) + "; status: " + str(response.status))
                break

            duration = self._get_duration(attempt)
            time.sleep(duration)
            self.print_log("Url: " + self._api.get_endpoint() + " Retry request: " + str(data))

    def flush_all(self):
        for stream in self._stream_keys.keys():

    def _get_duration(self, attempt):
        """
        Jitter implementation for exponential backoff

        :param attempt: count of attempt
        :type attempt: int
        """
        duration = self._retry_min_time * math.pow(2, attempt)
        duration = random.uniform(0.1, 1.0) * (duration - self._retry_min_time) + self._retry_min_time

        if duration > self._retry_max_time:
            duration = self._retry_max_time

        return duration

    def print_log(self, log_data):
        """
        Print debug information

        :param log_data: debug information
        :type log_data: str
        """
        if self._is_debug:
            self._logger.info(IronSourceAtomTracker._TAG + ": " + log_data)

    def graceful_kill(self, sig, frame):
        """
        Tracker exit handler
        :param frame: current stack frame
        :type frame: frame
        :type sig: OS SIGNAL number
        :param sig: integer
        """
        self._logger.info('Intercepted signal %s' % sig)
        self.stop()
