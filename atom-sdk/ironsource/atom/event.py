

class Event:
    """
        Event object

        :param stream: name of the stream
        :type stream: basestring
        :param data: data for sending
        :type data: basestring
    """
    def __init__(self, stream, data):
        self.stream = stream
        self.data = data
