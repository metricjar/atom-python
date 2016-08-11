class Response:
    def __init__(self, error, data, status):
        """
        Response information from server

        :param error: error information
        :type error: basestring
        :param data: response information data
        :type data: basestring
        :param status: response status from server
        :type status: int
        """
        self.error = error
        self.data = data
        self.status = status
