class Response:
    """
        Response information from server

        :param error: Error information
        :type error: object
        :param data: Response information data
        :type data: object
        :param status: Response status from server
        :type status: int
    """

    def __init__(self, error, data, status):
        self.error = error
        self.data = data
        self.status = status
