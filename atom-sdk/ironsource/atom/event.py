class Event:
    """
        Event object - Holds a single atom event data

        :param stream: atom stream name
        :type stream: basestring
        :param data: payload date to send
        :type data: basestring
    """

    def __init__(self, stream, data):
        self.stream = stream
        self.data = data
