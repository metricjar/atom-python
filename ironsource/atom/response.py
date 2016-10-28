class Response:
    """
        Response information from server

        :param error: error information
        :type error: object
        :param data: response information data
        :type data: object
        :param status: response status from server
        :type status: int
    """
    def __init__(self, error, data, status):

        self.error = error
        self.data = data
        self.status = status
