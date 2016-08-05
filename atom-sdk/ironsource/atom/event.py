

class Event:
    def __init__(self, stream, data, auth_key):
        self._stream = stream
        self._data = data
        self._auth_key = auth_key