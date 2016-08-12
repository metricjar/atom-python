import json
import hmac
import sys
import logging
import hashlib

from ironsource.atom.request import Request


class IronSourceAtom:
    _TAG = "IronSourceAtom"

    _SDK_VERSION = "1.1.0"
    _ATOM_URL = "http://track.atom-data.io/"

    def __init__(self):
        """AtomApi

        This is a lower level class that interacts with the service via HTTP REST API
        """
        self._endpoint = IronSourceAtom._ATOM_URL
        self._auth_key = ""

        self._is_debug = False

        self._init_headers()

        # init default logger
        self._logger = logging.getLogger()
        self._logger.setLevel(logging.DEBUG)

        stream_object = logging.StreamHandler(sys.stdout)
        stream_object.setLevel(logging.DEBUG)
        logger_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        stream_object.setFormatter(logger_formatter)
        self._logger.addHandler(stream_object)

    def _init_headers(self):
        """
        Init header map data
        """
        self._headers = {
            "x-ironsource-atom-sdk-type": "python",
            "x-ironsource-atom-sdk-version": IronSourceAtom._SDK_VERSION
        }

    def set_logger(self, logger):  # pragma: no cover
        """
        Set custom logger

        :param logger: custom logger instance
        :type logger: logging.Logger
        """
        self._logger = logger

    def enable_debug(self, is_debug):  # pragma: no cover
        """
        Enabling debug information

        :param is_debug: enable print debug inforamtion
        :type is_debug: bool
        """
        self._is_debug = is_debug

    def set_auth(self, auth_key):
        """
        Init authentication key

        :param auth_key: secret ket for streams
        :type auth_key: basestring
        """
        self._auth_key = auth_key

    def set_endpoint(self, endpoint):
        """
        Init server url

        :param endpoint: host name
        :type endpoint: basestring
        """
        self._endpoint = endpoint

    def get_endpoint(self):
        """
        Get current server url

        :rtype basestring
        """
        return self._endpoint

    def get_auth(self):
        """
        Get auth key

        :rtype basestring
        """
        return self._auth_key

    def put_event(self, stream, data, method="POST", auth_key=""):
        """A higher level method to send data

        This method exposes two ways of sending your events. Either by HTTP(s) POST or GET.

        :param method: the HTTP(s) method to use when sending data - default is POST
        :type method: str
        :param stream: the stream name
        :type stream: str
        :param data: a string of data to send to the server
        :type data: str
        :param auth_key: a string of data to send to the server
        :type auth_key: str

        :return: requests response object
        """

        if len(auth_key) == 0:
            auth_key = self._auth_key

        request_data = self._get_request_data(stream, auth_key, data)

        return self._sendData(url=self._endpoint, data=request_data, method=method,
                              headers=self._headers)

    def put_events(self, stream, data, auth_key=""):
        """A higher level method to send bulks of data

        This method received a list of dicts and transforms them into JSON objects and sends them
        to the service using HTTP(s) POST.

        :param stream: the stream name
        :type stream: str
        :param data: a string of data to send to the server
        :type data: str
        :param auth_key: a string of data to send to the server
        :type auth_key: str

        :return: requests response object
        """
        if not isinstance(data, list):
            raise Exception("data has to be of data type list")

        if len(auth_key) == 0:
            auth_key = self._auth_key

        data = json.dumps(data)

        request_data = self._get_request_data(stream, auth_key, data, bulk=True)

        return self._sendData(url=self._endpoint + "bulk", data=request_data, method="post",
                              headers=self._headers)

    def _get_request_data(self, stream, auth_key, data, bulk=False):
        """
        Create json data string from input data

        :param stream: the stream name
        :type stream: basestring
        :param auth_key: secret key for stream
        :type auth_key: basestring
        :param data: data to send to the server
        :type data: basestring
        :param bulk: send data by bulk
        :type bulk: bool

        :return: json data
        :rtype: basestring
        """
        request_data = {"table": stream, "data": data}

        if len(auth_key) != 0:

            auth_key_bytes = bytearray()
            auth_key_bytes.extend(auth_key)

            request_data["auth"] = hmac.new(auth_key_bytes, msg=data, digestmod=hashlib.sha256).hexdigest()

        if bulk:
            request_data["bulk"] = True

        return json.dumps(request_data)

    def _sendData(self, url, data, method, headers):
        """
        :param stream: the stream name
        :type stream: basestring
        :param data: data to send to the server
        :type data: basestring
        :param method: type of HTTP request
        :type method: basestring

        :return: response from server
        :rtype: Response
        """
        request = Request(url, data, headers)

        if method.lower() == "get":
            return request.get()
        else:
            return request.post()

    def _print_log(self, log_info):  # pragma: no cover
        """
        Print debug information

        :param log_info: debug information
        :type log_info: basestring
        """
        if self._is_debug:
            self._logger.info(IronSourceAtom._TAG + ": " + log_info)
