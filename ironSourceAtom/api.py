import requests
import json
import base64

from ironSourceAtom import __version__

SDK_VERSION = __version__
ATOM_URL = "http://track.atom-data.io/"


class AtomApi(object):
    """AtomApi

    This is a lower level class that interacts with the service via HTTP REST API

    :param url: atom URL
    :type url: str
    :param auth: Authentication key
    :type auth: str
    """
    def __init__(self, url=ATOM_URL, auth=None):
        self.url = url
        self.auth = auth
        self.headers = {
            "x-ironsource-atom-sdk-type": "python",
            "x-ironsource-atom-sdk-version": SDK_VERSION
        }
        self.session = requests.Session()

    def _request_get(self, stream, data):
        """Request with GET method

        This method encasulates the data object with base64 encoding and sends it to the service.
        Sends the request according to the REST API specification

        :param stream: the stream name
        :type stream: str
        :param data: a string of data to send to the service
        :type data: str

        :return: requests response object
        """
        payload = {"table": stream, "data": data}
        if self.auth:
            payload['auth'] = self.auth

        base64_str = base64.encodestring(('%s' % (json.dumps(payload))).encode()).decode().replace('\n', '')

        payload = {'data': base64_str}
        return self.session.get(self.url, params=payload, headers=self.headers)

    def _request_post(self, stream, data, bulk=False):
        """Request with POST method

        This method encapsulates the data and sends it to the service.
        Sends the request according to the REST API specification.

        :param stream: the stream name
        :type stream: str
        :param data: a string of data to send to the service
        :type data: str
        :param bulk: specify if the data is bulked
        :type bulk: bool

        :return: requests response object
        """
        payload = {"table": stream, "data": data}

        if self.auth:
            payload['auth'] = self.auth

        if bulk:
            payload['bulk'] = True

        return self.session.post(url=self.url, data=json.dumps(payload), headers=self.headers)

    def put_event(self, stream, data, method="POST"):
        """A higher level method to send data

        This method exposes two ways of sending your events. Either by HTTP(s) POST or GET.

        :param method: the HTTP(s) method to use when sending data - default is POST
        :type method: str
        :param stream: the stream name
        :type stream: str
        :param data: a string of data to send to the server
        :type data: str

        :return: requests response object
        """
        if method.lower() == "get":
            return self._request_get(stream=stream, data=data)
        else:
            return self._request_post(stream=stream, data=data)

    def put_events(self, stream, data):
        """A higher level method to send bulks of data

        This method received a list of dicts and transforms them into JSON objects and sends them
        to the service using HTTP(s) POST.

        :param stream: the stream name
        :type stream: str
        :param data: a string of data to send to the server
        :type data: str

        :return: requests response object
        """

        if not isinstance(data, list):
            raise Exception("data has to be of data type list")

        data = json.dumps(data)

        return self._request_post(stream=stream, data=data, bulk=True)
