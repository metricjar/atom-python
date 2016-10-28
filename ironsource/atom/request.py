import base64
import requests.exceptions
from ironsource.atom.response import Response


class Request:
    """
        Wrapper for HTTP requests to Atom API
    """

    def __init__(self, endpoint, data, session):
        """
        :param endpoint: Atom API endpoint
        :type endpoint: str
        :param data: Data that will be sent to server
        :type data: str
        :param session: requests.Session object
        :type session: function
        """
        self._url = endpoint
        self._data = data
        self._session = session

    def get(self):
        """
        Request with GET method

        This method encapsulates the data object with base64 encoding and sends it to the service.
        Sends the request according to the REST API specification

        :return: Response object from server
        :rtype: Response
        """

        base64_str = base64.encodestring(('%s' % self._data).encode()).decode().replace('\n', '')
        params = {'data': base64_str}

        try:
            response = self._session.get(self._url, params=params)
        except requests.exceptions.ConnectionError:  # pragma: no cover
            return Response("No connection to server", None, 500)
        except requests.exceptions.RequestException as ex:  # pragma: no cover
            return Response(ex, None, 400)
        if 200 <= response.status_code < 400:
            return Response(None, response.content, response.status_code)
        else:
            return Response(response.content, None, response.status_code)

    def post(self):
        """
        Request with POST method

        This method encapsulates the data and sends it to the service.
        Sends the request according to the REST API specification.

        :return: Response object from server
        :rtype: Response
        """
        try:
            response = self._session.post(url=self._url, data=self._data)
        except requests.exceptions.ConnectionError:  # pragma: no cover
            return Response("No connection to server", None, 500)
        except requests.exceptions.RequestException as ex:  # pragma: no cover
            return Response(ex, None, 400)

        if 200 <= response.status_code < 400:
            return Response(None, response.content, response.status_code)
        else:
            return Response(response.content, None, response.status_code)
