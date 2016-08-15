import requests
import base64

from requests.exceptions import RequestException

from ironsource.atom.response import Response


class Request:
    """
        Construct for requester

        :param url: server url
        :type url: basestring
        :param data: data ot send to the server
        :type data: basestring
        :param headers: list of header information
        :type headers: list(String)
    """
    def __init__(self, url, data, headers):
        self._url = url
        self._data = data
        self._headers = headers

        self._session = requests.Session()

    def get(self):
        """Request with GET method

        This method encapsulates the data object with base64 encoding and sends it to the service.
        Sends the request according to the REST API specification

        :return: Response object from server
        :rtype: Response
        """

        base64_str = base64.encodestring(('%s' % (self._data)).encode()).decode().replace('\n', '')
        params = {'data': base64_str}

        try:
            response = self._session.get(self._url, params=params, headers=self._headers)
        except RequestException as ex:  # pragma: no cover
            if ex.response:
                return Response(response.content, None, response.status_code)
            else:
                return Response("Failed to establish a new connection", None, -1)

        if 200 <= response.status_code < 400:
            return Response(None, response.content, response.status_code)
        else:
            return Response(response.content, None, response.status_code)

    def post(self):
        """Request with POST method

        This method encapsulates the data and sends it to the service.
        Sends the request according to the REST API specification.

        :return: Response object from server
        :rtype: Response
        """
        try:
            response = self._session.post(url=self._url, data=self._data, headers=self._headers)
        except RequestException as ex:  # pragma: no cover
            if ex.response:
                return Response(response.content, None, response.status_code)
            else:
                return Response("Failed to establish a new connection", None, -1)

        if 200 <= response.status_code < 400:
            return Response(None, response.content, response.status_code)
        else:
            return Response(response.content, None, response.status_code)
