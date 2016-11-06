import json
import signal

from ironsource.atom.ironsource_atom import IronSourceAtom
from ironsource.atom.queue_event_storage import QueueEventStorage
from ironsource.atom.batch_event_pool import BatchEventPool
from ironsource.atom.event import Event
import ironsource.atom.atom_logger as logger
import ironsource.atom.config as config
import time
import random

from threading import Lock
from threading import Thread


class IronSourceAtomTracker:
    """
       ironSource Atom high level API class (Tracker), supports: track() and flush()
    """
    TAG = "IronSourceAtomTracker"

    def __init__(self,
                 batch_worker_count=config.BATCH_WORKER_COUNT,
                 batch_pool_size=config.BATCH_POOL_SIZE,
                 event_backlog=None,
                 backlog_size=config.BACKLOG_SIZE,
                 flush_interval=config.FLUSH_INTERVAL,
                 retry_max_time=config.RETRY_MAX_TIME,
                 retry_max_count=config.RETRY_MAX_COUNT,
                 batch_size=config.BATCH_SIZE,
                 batch_bytes_size=config.BATCH_BYTES_SIZE,
                 is_debug=False,
                 endpoint=config.ATOM_ENDPOINT,
                 auth_key="",
                 callback=None,
                 retry_forever=config.RETRY_FOREVER):
        """
        Tracker init function

        :param batch_worker_count: Optional, Number of workers(threads) for BatchEventPool
        :type  batch_worker_count: int
        :param batch_pool_size:    Optional, Number of events to hold in BatchEventPool
        :type  batch_pool_size:    int
        :param event_backlog:      Optional, Custom EventStorage implementation
        :type  event_backlog:      object
        :param backlog_size:       Optional, Backlog queue size (EventStorage ABC implementation)
        :type  backlog_size:       int
        :param flush_interval:     Optional, Tracker flush interval in milliseconds (default 10000)
        :type  flush_interval:     int
        :param retry_max_time:     Optional, Retry max time in seconds
        :type  retry_max_time:     int
        :param retry_max_count:    Optional, Maximum number of retries in seconds
        :type  retry_max_count:    int
        :param batch_size:         Optional, Amount of events in every batch (bulk) (default: 500)
        :type  batch_size:         int
        :param batch_bytes_size:   Optional, Size of each batch (bulk) in bytes (default: 64KB)
        :type  batch_bytes_size:   int
        :param is_debug:           Optional, Enable printing of debug information
        :type  is_debug:           bool
        :param endpoint:           Optional, Atom endpoint
        :type  endpoint:           str
        :param auth_key:           Optional, Default auth key to use (when none is provided in .track)
        :type  auth_key:           str
        :param callback:           Optional, callback to be called on error (Client 400/ Server 500)
        :type  callback:           function
        :param retry_forever:      Optional, should the worker in BatchEventPool retry forever on server error (500)
        :type  retry_forever:      bool
        """

        # Init Atom basic SDK
        self._is_debug = is_debug
        # For debug printing
        self._debug_counter = 0
        self._atom = IronSourceAtom(endpoint=endpoint, is_debug=self._is_debug, auth_key=auth_key)
        self._logger = logger.get_logger(debug=self._is_debug)

        # Optional callback to be called on error, convention: time, status, error_msg, data
        self._callback = callback if callable(callback) else lambda timestamp, status, error_msg, data: None

        self._is_run_worker = True
        self._flush_all = False
        self._alive = True

        # Lock of accessing the stream_keys dict
        self._data_lock = Lock()

        # Streams to keys map
        self._stream_keys = {}

        # Retry with exponential backoff config
        # Retry max time
        if not isinstance(retry_max_time, int) or retry_max_time < 120:
            self._logger.warning("Retry Max Time must be 120 or greater! Setting default: {}"
                                 .format(config.RETRY_MAX_TIME))
            retry_max_time = config.RETRY_MAX_TIME
        self._retry_max_time = retry_max_time

        # Retry max count
        if not isinstance(retry_max_count, int) or retry_max_count < 1:
            self._logger.warning("Retry Max Count must be 1 or greater! Setting default: {}"
                                 .format(config.RETRY_MAX_COUNT))
            retry_max_count = config.RETRY_MAX_COUNT
        self._retry_max_count = retry_max_count

        # Batch size
        if not isinstance(batch_size, int) or batch_size < 1:
            self._logger.warning("Batch Size must be 1 or greater! Setting default: {}"
                                 .format(config.BATCH_SIZE))
            batch_size = config.BATCH_SIZE
        self._batch_size = batch_size

        # Batch bytes size
        if not isinstance(batch_bytes_size, int) or batch_bytes_size < 1:
            self._logger.warning("Batch Bytes Size must be 1 or greater! Setting default: {}"
                                 .format(config.BATCH_BYTES_SIZE))
            batch_bytes_size = config.BATCH_BYTES_SIZE
        self._batch_bytes_size = batch_bytes_size

        # Flush Interval
        if not isinstance(flush_interval, int) or flush_interval < 1000:
            self._logger.warning("Flush Interval must be 1000 or greater! Setting default: {}"
                                 .format(config.FLUSH_INTERVAL))
            flush_interval = config.FLUSH_INTERVAL
        self._flush_interval = flush_interval

        # Holds the events after .track method
        self._event_backlog = event_backlog if event_backlog else QueueEventStorage(queue_size=backlog_size)

        # Holds batch of events for each stream and sends them using {thread_count} workers
        self._batch_event_pool = BatchEventPool(thread_count=batch_worker_count,
                                                max_events=batch_pool_size)

        # Retry forever on server error (500)
        self._retry_forever = retry_forever

        # Start the handler thread - daemon since we want to exit even if it didn't stop yet
        handler_thread = Thread(target=self._tracker_handler)
        handler_thread.daemon = True
        handler_thread.start()

        # Start the thread that handles periodic flushing
        timer_thread = Thread(target=self._flush_peroidcly)
        timer_thread.daemon = True
        timer_thread.start()

        # Intercept exit signals
        signal.signal(signal.SIGTERM, self._graceful_kill)
        signal.signal(signal.SIGINT, self._graceful_kill)

    def stop(self):
        """
        Stop worker thread and event_pool thread's
        """
        self._logger.info("Flushing all data and killing the tracker in 5 seconds...")
        self._flush_all = True
        self._alive = False
        i = 0
        while True:
            # Check if everything is empty or 5 seconds has passed
            if self._batch_event_pool.is_empty() and self._event_backlog.is_empty() or i == 5:
                self._logger.warning("BatchPool and Backlog are empty or 5 seconds have passed, killing the tracker")
                self._is_run_worker = False
                self._batch_event_pool.stop()
                break
            i += 1
            time.sleep(1)

    def set_debug(self, is_debug):  # pragma: no cover
        """
        Enable / Disable debug

        :param is_debug: Enable printing of debug information
        :type is_debug: bool
        """
        self._is_debug = is_debug if isinstance(is_debug, bool) else False
        self._logger = logger.get_logger(debug=self._is_debug)
        self._atom.set_debug(self._is_debug)

    def track(self, stream, data, auth_key=""):
        """
        Track event

        :param stream: Atom stream name
        :type stream: str
        :param data: Data to send (payload) (dict or string)
        :type data: object
        :param auth_key: HMAC auth key for stream
        :type auth_key: str
        """
        if len(auth_key) == 0:
            auth_key = self._atom.get_auth()

        if not isinstance(data, str):
            try:
                data = json.dumps(data)
            except TypeError as e:
                self._error_log(0, time.time(), 400, str(e), data)
                return

        with self._data_lock:
            if stream not in self._stream_keys:
                self._stream_keys[stream] = auth_key
            self._event_backlog.add_event(Event(stream, data))
            self._debug_counter += 1

    def flush(self):
        """
        Flush data from all streams
        """
        self._flush_all = True

    def _flush_peroidcly(self):
        """
        Flush everything every {flush_interval}

        Note: the time.time() is used cause python is not accurate enough and adds a delay
        when using time.sleep(x) (where x is a constant)
        """
        next_call = time.time()
        i = 0
        while self._is_run_worker:
            if i == 10000:
                i = 0
            # Divide by 1000 since flush_interval is provided in milliseconds
            next_call += self._flush_interval / 1000
            # This part is here only for better debugging
            if i % 2 == 0:
                self._logger.debug("Flushing In {} Seconds".format(next_call - time.time()))
            i += 1
            try:
                time.sleep(next_call - time.time())
                self.flush()
            except (IOError, ValueError) as e:
                # Can happen after sleep
                self._logger.error("Timer error: {}".format(str(e.args)))
                next_call = time.time()

    def _tracker_handler(self):
        """
        Main tracker function, handles flushing based on given conditions
        """
        # Buffer between backlog and batch pool
        events_buffer = {}
        # Dict to hold events size for every stream
        events_size = {}
        self._logger.info("Tracker Handler Started")

        def flush_data(stream, auth_key):
            # This 'if' is needed for the flush_all case
            if stream in events_buffer and len(events_buffer[stream]) > 0:
                temp_buffer = list(events_buffer[stream])
                del events_buffer[stream][:]
                events_size[stream] = 0
                self._batch_event_pool.add_event(lambda: self._flush_data(stream, auth_key, temp_buffer))

        while self._is_run_worker:
            if self._event_backlog.is_empty():
                time.sleep(2)

            if self._flush_all:
                for stream_name, stream_key in self._stream_keys.items():
                    flush_data(stream_name, stream_key)
                if self._alive:
                    self._flush_all = False
            else:
                for stream_name, stream_key in self._stream_keys.items():
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

                    if events_size[stream_name] >= self._batch_bytes_size:
                        flush_data(stream_name, auth_key=stream_key)

                    if len(events_buffer[stream_name]) >= self._batch_size:
                        flush_data(stream_name, auth_key=stream_key)
        self._logger.info("Tracker handler stopped")

    def _flush_data(self, stream, auth_key, data):
        """
        Send data to server using IronSource Atom Low-level API

        NOTE: this function is passed a lambda to the BatchEventPool so it might continue running if it was
        triggered already even after a graceful killing for at least (retry_max_count) times
        """
        attempt = 1

        while True:
            try:
                response = self._atom.put_events(stream, data=data, auth_key=auth_key)
            except Exception as e:
                self._error_log(attempt, time.time(), 400, str(e), data)
                return

            # Response on first try
            if attempt == 1:
                self._logger.debug('Got Status: {}; Data: {}'.format(str(response.status), str(data)))

            # Status 200 - OK or 400 - Client Error
            if 200 <= response.status < 500:
                if 200 <= response.status < 400:
                    if self._debug_counter >= 1000:
                        self._logger.info('Tracked 1000 events')
                        self._logger.info('Status: {}; Response: {}; Error: {}'.format(str(response.status),
                                                                                       str(response.data),
                                                                                       str(response.error)))
                        self._debug_counter = 0
                else:
                    # 400
                    self._error_log(attempt, time.time(), response.status, response.error, data)
                return

            # Server Error >= 500:
            # This should run forever (when we get a 500) unless retry_forever is False
            # In this case we call error_log() function and data will be lost (you can save it with the callback)
            if not self._retry_forever and attempt == self._retry_max_count:
                self._error_log(attempt, time.time(), 500, "Retry Max Count has been reached, discarding data", data)
                break
            # Retry with exponential backoff
            duration = self._get_duration(attempt)
            self._error_log(attempt, time.time(), response.status, response.error, data)
            self._logger.info("Retry duration: {}".format(duration))
            attempt += 1
            time.sleep(duration)

    def _get_duration(self, attempt):
        """
        Exponential back-off + Full Jitter

        :param attempt: attempt number
        :type attempt: int
        """
        exponential_backoff = min(self._retry_max_time, pow(2, attempt) * config.RETRY_EXPO_BACKOFF_BASE)
        return random.uniform(0, exponential_backoff)

    def _graceful_kill(self, sig, frame):
        """
        Tracker exit handler
        :param frame: current stack frame
        :type frame: frame
        :param sig: integer
        :type sig: OS signal number
        """
        self._logger.info('Intercepted signal %s' % sig)
        if not self._is_run_worker:
            return
        self.stop()

    def _error_log(self, attempt, unix_time=None, status=None, error_msg=None, sent_data=None):
        """
        Log an error and send it to a callback function (if defined by user)
        :param attempt: Sending attempt to atom
        :type  attempt: int
        :param unix_time: Unix(epoch) timestamp
        :type  unix_time: float
        :param status: HTTP status
        :type  status: int
        :param error_msg: Error msg from server
        :type  error_msg: str
        :param sent_data: Data that was sent to server
        :type  sent_data: object
        """
        try:
            self._callback(unix_time, status, error_msg, sent_data)
        except TypeError as e:
            self._logger.error('Wrong arguments given to callback function: {}'.format(e))

        self._logger.error("Error: {}; Status: {}; Attempt: {}; For Data: {:.50}...".format(error_msg,
                                                                                            status,
                                                                                            attempt,
                                                                                            sent_data))
