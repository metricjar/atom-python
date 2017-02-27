class Response:
    """
        Response information from Atom server
    """

    def __init__(self, error, data, status, raw_response):
        """
        :param error: Error information
        :type error: object
        :param data: Response information data
        :type data: object
        :param status: Response status from server
        :type status: int
        :param raw_response: Original response object
        :type raw_response: object
        """
        self.error = error
        self.data = data
        self.status = status
        self.raw_response = raw_response
