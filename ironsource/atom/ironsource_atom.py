import json
import hmac
import sys
import logging
import hashlib

from ironsource.atom.request import Request


class IronSourceAtom:
    """
       AtomApi

       ironSource Atom low level API. supports put_event() and put_events() methods.
    """

    _TAG = "IronSourceAtom"

    _SDK_VERSION = "1.1.2"
    _ATOM_URL = "http://track.atom-data.io/"

    def __init__(self):

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

        :param is_debug: enable printing of debug information
        :type is_debug: bool
        """
        self._is_debug = is_debug

    def set_auth(self, auth_key):
        """
        Set HMAC authentication key

        :param auth_key: HMAC auth key for your stream
        :type auth_key: str
        """
        self._auth_key = auth_key

    def set_endpoint(self, endpoint):
        """
        Set Atom Endpoint url

        :param endpoint: Atom API endpoint
        :type endpoint: str
        """
        self._endpoint = endpoint

    def get_endpoint(self):
        """
        Get current Atom API endpoint

        :rtype: str
        """
        return self._endpoint

    def get_auth(self):
        """
        Get HMAC authentication key

        :rtype: str
        """
        return self._auth_key

    def put_event(self, stream, data, method="POST", auth_key=""):
        """Send a single event to Atom API

        This method exposes two ways of sending your events. Either by HTTP(s) POST or GET.

        :param method: the HTTP(s) method to use when sending data - default is POST
        :type method: str
        :param stream: Atom Stream name
        :type stream: str
        :param data: a string of data (payload) to send to the server
        :type data: str
        :param auth_key: hmac auth key
        :type auth_key: str

        :return: requests response object
        """

        if len(auth_key) == 0:
            auth_key = self._auth_key

        request_data = self.get_request_data(stream, auth_key, data)

        return self.send_data(url=self._endpoint, data=request_data, method=method,
                              headers=self._headers)

    def put_events(self, stream, data, auth_key=""):
        """Send multiple events (batch) to Atom API

        This method receives a list of dictionaries, transforms them into JSON objects and sends them
        to Atom using HTTP(s) POST.

        :param stream: Atom Stream name
        :type stream: str
        :param data: a string of data to send to the server
        :type data: list(str)
        :param auth_key: a string of data to send to the server
        :type auth_key: str

        :return: requests response object
        """
        if not isinstance(data, list):
            raise Exception("data has to be of data type list")

        if len(auth_key) == 0:
            auth_key = self._auth_key

        data = json.dumps(data)

        request_data = self.get_request_data(stream, auth_key, data, bulk=True)

        return self.send_data(url=self._endpoint + "bulk", data=request_data, method="post",
                              headers=self._headers)

    @staticmethod
    def get_request_data(stream, auth_key, data, bulk=False):
        """
        Create json data string from input data

        :param stream: the stream name
        :type stream: str
        :param auth_key: secret key for stream
        :type auth_key: str
        :param data: data to send to the server
        :type data: str
        :param bulk: send data by bulk
        :type bulk: bool

        :return: json data
        :rtype: str
        """
        request_data = {"table": stream, "data": data}

        if len(auth_key) != 0:
            request_data["auth"] = hmac.new(bytes(auth_key.encode("utf-8")),
                                            msg=data.encode("utf-8"),
                                            digestmod=hashlib.sha256).hexdigest()

        if bulk:
            request_data["bulk"] = True

        return json.dumps(request_data)

    @staticmethod
    def send_data(url, data, method, headers):
        """
        :param headers: HTTP request headers
        :type headers: dict
        :param url: Atom API endpoint
        :type url: str
        :param data: data to send to the server
        :type data: str
        :param method: type of HTTP request
        :type method: str

        :return: response from server
        :rtype: Response
        """
        request = Request(url, data, headers)

        if method.lower() == "get":
            return request.get()
        else:
            return request.post()

    def print_log(self, log_info):  # pragma: no cover
        """
        Print debug information

        :param log_info: debug information
        :type log_info: str
        """
        if self._is_debug:
            self._logger.info(IronSourceAtom._TAG + ": " + log_info)
