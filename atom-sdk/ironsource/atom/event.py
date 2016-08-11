

class Event:
    def __init__(self, stream, data):
        """
        Event object

        :param stream: name of the stream
        :type stream: basestring
        :param data: data for sending
        :type data: basestring
        """
        self.stream = stream
        self.data = data
