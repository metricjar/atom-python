import requests
import json
import base64

SDK_VERSION = "1.0.0"
ATOM_URL = "http://track.atom-data.io/"


class AtomApi(object):

    def __init__(self, url=ATOM_URL, auth=None):

        self.url = url
        self.auth = auth
        self.headers = {
            "x-ironsource-atom-sdk-type": "python",
            "x-ironsource-atom-sdk-version": SDK_VERSION
        }
        self.session = requests.Session()

    def _request_get(self, stream, data):
        payload = {"table": stream, "data": data}
        if self.auth:
            payload['auth'] = self.auth

        base64_str = base64.encodestring(('%s' % (json.dumps(payload))).encode()).decode().replace('\n', '')

        payload = {'data': base64_str}
        return self.session.get(self.url, params=payload, headers=self.headers)

    def _request_post(self, stream, data):
        payload = {"table": stream, "data": data}
        if self.auth:
            payload['auth'] = self.auth

        return self.session.post(url=self.url, data=json.dumps(payload), headers=self.headers)

    def put_event(self, stream, data, method="POST"):
        if method.lower() == "get":
            return self._request_get(stream=stream, data=data)
        else:
            return self._request_post(stream=stream, data=data)
