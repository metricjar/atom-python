import json
import hmac
import datetime
import requests
import hashlib
import ironsource.atom.atom_logger as logger
from ironsource.atom.request import Request
import ironsource.atom.config as config
import uuid
import os


class IronSourceAtom:
    """
        ironSource Atom low level API. supports put_event() and put_events() methods.
    """

    TAG = "IronSourceAtom"

    def __init__(self, is_debug=False, endpoint=config.ATOM_ENDPOINT, auth_key="", request_timeout=60,
                 debug_to_file=False,
                 debug_file_path=config.DEBUG_FILE_PATH):
        """
        Atom class init function

        :param is_debug:            Optional, Enable/Disable debug
        :type  is_debug:            bool
        :param endpoint:            Optional, Atom API Endpoint
        :type  endpoint:            str
        :param auth_key:            Optional, Atom auth key
        :type  auth_key:            str
        :param request_timeout:     Optional, request timeout (default: 60)
        :type  request_timeout:     int
        :param debug_to_file:       Optional, Should the Tracker write the request and response objects to file
        :type  debug_to_file:       bool
        :param debug_file_path:     Optional, the path to the debug file (debug_to_file must be True) (default: /tmp)
        :type  debug_file_path:     str

        """

        self._endpoint = endpoint
        self._auth_key = auth_key
        self._is_debug = is_debug
        self._timeout = request_timeout

        self._headers = {
            'x-ironsource-atom-sdk-type': 'python',
            'x-ironsource-atom-sdk-version': config.SDK_VERSION,
            'Content-Type': 'application/json'
        }

        # init logger
        self._logger = logger.get_logger(debug=self._is_debug)

        self._debug_to_file = debug_to_file
        if self._debug_to_file:
            if os.path.isdir(debug_file_path) and os.access(debug_file_path, os.W_OK | os.R_OK):
                self._debug_file_path = debug_file_path
            else:
                self._debug_file_path = config.DEBUG_FILE_PATH
                self._logger.error("No Read & Write access to the supplied log file path, setting default: {}"
                                   .format(config.DEBUG_FILE_PATH))
            now = datetime.datetime.now()
            log_file_name = self._debug_file_path + "atom-raw.{day}-{month}.json".format(day=now.day, month=now.month)
            self._raw_logger = logger.get_logger(name="AtomRawLogger", file_name=log_file_name)

    def set_debug(self, is_debug):  # pragma: no cover
        """
        Enable / Disable debug

        :param is_debug: Enable printing of debug information
        :type is_debug: bool
        """
        self._is_debug = is_debug if isinstance(is_debug, bool) else False
        self._logger = logger.get_logger(debug=self._is_debug)

    def get_auth(self):
        """
        Get HMAC authentication key

        :rtype: str
        """
        return self._auth_key

    def put_event(self, stream, data, method="POST", auth_key=""):
        """Send a single event to Atom API

        This method exposes two ways of sending your events. Either by HTTP(s) POST or GET.

        :param method: The HTTP(s) method to use when sending data - default is POST
        :type method: str
        :param stream: Atom Stream name
        :type stream: str
        :param data: Single data (payload) event that will be sent to the server (string or dict)
        :type data: object
        :param auth_key: Hmac auth key
        :type auth_key: str

        :return: requests response object
        """
        if not data or not stream:
            raise Exception("Stream and/or Data are missing")
        if len(auth_key) == 0:
            auth_key = self._auth_key

        request_time = datetime.datetime.now().isoformat()
        request_data = self.create_request_data(stream, auth_key, data)
        response = self.send_data(url=self._endpoint, data=request_data, method=method, headers=self._headers,
                                  timeout=self._timeout)
        if self._debug_to_file:
            self._session_to_file(response, request_time)
        return response

    def put_events(self, stream, data, auth_key=""):
        """Send multiple events (batch) to Atom API

        This method receives a list of dictionaries, transforms them into JSON objects and sends them
        to Atom using HTTP(s) POST.

        :param stream: Atom Stream name
        :type stream: str
        :param data: List of strings or dictionaries that will be sent to Atom
        :type data: list(object)
        :param auth_key: Optional, Hmac auth key
        :type auth_key: str

        :return: requests response object
        """
        if not isinstance(data, list) or not data:
            raise Exception("Data has to be of a non-empty list")
        if not stream:
            raise Exception("Stream is required")
        if len(auth_key) == 0:
            auth_key = self._auth_key

        data = json.dumps(data)
        request_data = self.create_request_data(stream, auth_key, data, batch=True)

        request_time = datetime.datetime.now().isoformat()
        response = self.send_data(url=self._endpoint + "bulk", data=request_data, method="post", headers=self._headers,
                                  timeout=self._timeout)
        if self._debug_to_file:
            self._session_to_file(response, request_time)
        return response

    @staticmethod
    def create_request_data(stream, auth_key, data, batch=False):
        """
        Create json data string from input data

        :param stream: Atom stream name
        :type stream: str
        :param auth_key: Hmac auth key
        :type auth_key: str
        :param data: Data that will be sent to the Atom
        :type data: object
        :param batch: Send data by batch(bulk)
        :type batch: bool
        :return: Serialized data as JSON
        :rtype: str
        """
        if not isinstance(data, str):
            try:
                data = json.dumps(data)
            except TypeError:
                raise Exception("Cannot Encode JSON")

        request_data = {"table": stream, "data": data}

        if len(auth_key) != 0:
            request_data["auth"] = hmac.new(bytes(auth_key.encode("utf-8")),
                                            msg=data.encode("utf-8"),
                                            digestmod=hashlib.sha256).hexdigest()

        if batch:
            request_data["bulk"] = True

        return json.dumps(request_data)

    @staticmethod
    def send_data(url, data, method, headers, timeout):
        """
        :param url: Atom API endpoint
        :type url: str
        :param data: Data that will be sent to Atom
        :type data: str
        :param method: Type of HTTP request
        :type method: str
        :param headers: HTTP request headers
        :type headers: dict
        :param timeout: request timeout

        :return: response from server
        :rtype: Response
        """
        with requests.Session() as session:
            session.headers.update(headers)
            request = Request(url, data, session, timeout)
            if method.lower() == "get":
                return request.get()
            else:
                return request.post()

    def _session_to_file(self, response, request_time):
        """
        Writes SDK request and response to JSON file in the following format:
        [{req},{res}...]
        :param request_time: request time
        :param response: The 'requests' lib response object (including the original request)
        """
        raw_request = response.raw_response.request
        request_data = raw_request.body if raw_request.body is not None else '"{}"'.format(raw_request.path_url)
        session_id = uuid.uuid4()
        # self._raw_logger.emit("hi")
        self._raw_logger.info('''{"request": {"id": "%s", "requestTime": "%s", "data": %s, "headers": %s}}''' %
                              (session_id,
                               request_time,
                               request_data,
                               json.dumps(str(raw_request.headers))
                               ))
        # Format response
        response_headers = json.dumps(str(response.raw_response.headers)) \
            if hasattr(response.raw_response, "headers") else "\"None\""
        response_body = response.data if response.data is not None else response.error
        try:
            response_body = json.loads(response_body)
        except ValueError:
            pass
        # There is no consistency at API response on v1
        if response.status == 401:
            response_body = str(response_body).replace("\"", "'")
        self._raw_logger.info(
            '''{"response": {"id": "%s", "responseTime": "%s", "body": "%s", "code": %s, "headers": %s}}''' %
            (session_id,
             datetime.datetime.now().isoformat(),
             response_body,
             response.status,
             response_headers))
