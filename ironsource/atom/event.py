class Event:
    """
        Event object - Holds a single atom event (inside EventStorage)

        :param stream: Atom stream name
        :type stream: basestring
        :param data: Payload data to send
        :type data: object
    """

    def __init__(self, stream, data):
        self.stream = stream
        self.data = data
