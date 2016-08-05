from ironsource_atom import IronSourceAtom


class IronSourceAtomTacker:
    _TAG = "IronSourceAtomTacker"

    _DEFAULT_BULK_SIZE = 500
    _DEFAULT_BULK_BYTES_SIZE = 64 * 1024

    _DEFAULT_FLUSH_INTERVAL = 1000

    def __init__(self):
        self._api = IronSourceAtom()
        self._is_debug = False

        self._bulk_size = IronSourceAtomTacker._DEFAULT_BULK_SIZE
        self._bulk_bytes_size = IronSourceAtomTacker._DEFAULT_BULK_BYTES_SIZE

        self._flush_interval = IronSourceAtomTacker._DEFAULT_FLUSH_INTERVAL
        # fixme
        self._event_manager = None

    def set_event_manager(self, event_manager):
        self._event_manager = event_manager

    def set_task_pool_size(self, tasks_pool_size):
        pass

    def set_task_workers_count(self, task_worker_count):
        pass

    def enable_debug(self, is_debug):
        self._is_debug = is_debug

    def set_endpoint(self, endpoint):
        self._api.set_endpoint(endpoint)

    def set_auth(self, auth_key):
        self._api.set_auth(auth_key)

    def set_bulk_size(self, bulk_size):
        self._bulk_size = bulk_size

    def set_bulk_bytes_size(self, bulk_bytes_size):
        self._bulk_bytes_size = bulk_bytes_size

    def set_flush_interval(self, flush_interval):
        self._flush_interval = flush_interval

    def track(self, stream, data, auth_key = ""):
        if len(auth_key) == 0:
            auth_key = self._api.get_auth()

        # fixme

    def flush(self):
        pass



    def _print_log(self, log_data):
        if self._is_debug:
            print IronSourceAtomTacker._TAG + ": " + log_data
