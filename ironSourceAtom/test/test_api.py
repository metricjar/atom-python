import responses
import json
import base64
import unittest

try:
    # python 3
    from urllib.parse import urlparse, quote
    from unittest.mock import MagicMock
except ImportError:
    # python 2
    from urlparse import urlparse
    from urllib import quote
    from mock import MagicMock

from ironSourceAtom import api


class TestApiGET(unittest.TestCase):

    def setUp(self):
        self.url = "http://track.atom-data.io/"
        self.data = {"event_name": "test", "id": "2"}
        self.stream = "streamname"
        self.atom_client = api.AtomApi()

    @responses.activate
    def test_api_get_calls(self):
        responses.add(responses.GET, self.url, json=self.data, status=200)
        self.atom_client._request_get(stream=self.stream, data=json.dumps(self.data))
        self.assertEqual(len(responses.calls), 1, len(responses.calls))

    @responses.activate
    def test_api_get_response(self):
        responses.add(responses.GET, self.url, json={"Status": "Ok"}, status=200)
        res = self.atom_client._request_get(stream=self.stream, data=json.dumps(self.data))
        self.assertEqual(res.json(), {"Status": "Ok"}, res)

    @responses.activate
    def test_api_get_base64(self):
        responses.add(responses.GET, self.url, json={"Status": "Ok"}, status=200)
        self.atom_client._request_get(stream=self.stream, data=json.dumps(self.data))

        # request should be in data param base64 encoded
        assembled_request = {'table': self.stream, 'data': json.dumps(self.data)}
        b64data = base64.encodestring(('%s' % (json.dumps(assembled_request))).encode()).decode().replace('\n', '')
        b64data = quote(b64data)

        expected_base64_url = 'http://track.atom-data.io/?data={base64encoded}'.format(base64encoded=b64data)
        self.assertEqual(responses.calls[0].request.url, expected_base64_url, responses.calls[0].request.url)

    @responses.activate
    def test_api_get_headers(self):
        responses.add(responses.GET, self.url, json={"Status": "Ok"}, status=200)
        self.atom_client._request_get(stream=self.stream, data=json.dumps(self.data))

        headers = responses.calls[0].request.headers

        self.assertIn("x-ironsource-atom-sdk-version", headers)
        self.assertIn("x-ironsource-atom-sdk-type", headers)

    @responses.activate
    def test_api_get_auth(self):
        responses.add(responses.GET, self.url, json={"Status": "Ok"}, status=200)
        self.atom_client = api.AtomApi(auth="my_auth_key")
        self.atom_client._request_get(stream=self.stream, data=json.dumps(self.data))

        url = responses.calls[0].request.url
        parsed_url = urlparse(url)
        query = parsed_url.query
        b64data = query[5:]
        b64data = base64.b64decode(b64data)
        b64data = json.loads(b64data.decode("utf-8"))

        self.assertIn("auth", b64data)


class TestApiPost(unittest.TestCase):

    def setUp(self):
        self.url = "http://track.atom-data.io/"
        self.data = {"event_name": "test", "id": "2"}
        self.stream = "streamname"
        self.atom_client = api.AtomApi()

    @responses.activate
    def test_api_post_calls(self):
        responses.add(responses.POST, self.url, json=self.data, status=200)
        self.atom_client._request_post(stream=self.stream, data=json.dumps(self.data))
        self.assertEqual(len(responses.calls), 1, len(responses.calls))

    @responses.activate
    def test_api_post_response(self):
        responses.add(responses.POST, self.url, json={"Status": "Ok"}, status=200)
        res = self.atom_client._request_post(stream=self.stream, data=json.dumps(self.data))
        self.assertEqual(res.json(), {"Status": "Ok"}, res)

    @responses.activate
    def test_api_post_headers(self):
        responses.add(responses.POST, self.url, json={"Status": "Ok"}, status=200)
        self.atom_client._request_post(stream=self.stream, data=json.dumps(self.data))

        headers = responses.calls[0].request.headers

        self.assertIn("x-ironsource-atom-sdk-version", headers)
        self.assertIn("x-ironsource-atom-sdk-type", headers)

    @responses.activate
    def test_api_post_auth(self):
        responses.add(responses.POST, self.url, json={"Status": "Ok"}, status=200)
        self.atom_client = api.AtomApi(auth="my_auth_key")
        self.atom_client._request_post(stream=self.stream, data=json.dumps(self.data))

        body = json.loads(responses.calls[0].request.body)
        self.assertIn("auth", body)


class TestPutEvent(unittest.TestCase):
    def setUp(self):
        self.url = "http://track.atom-data.io/"
        self.data = {"event_name": "test", "id": "2"}
        self.stream = "streamname"
        self.atom_client = api.AtomApi()

    @responses.activate
    def test_put_event_get(self):
        responses.add(responses.GET, self.url, json={"Status": "Ok"}, status=200)
        self.atom_client.put_event(stream=self.stream, data=json.dumps(self.data), method="get")

        self.assertEqual(responses.calls[0].request.method, "GET", "Method called should be GET")

    @responses.activate
    def test_put_event_post(self):
        responses.add(responses.POST, self.url, json={"Status": "Ok"}, status=200)
        self.atom_client.put_event(stream=self.stream, data=json.dumps(self.data), method="POST")

        self.assertEqual(responses.calls[0].request.method, "POST")


class TestPutEvents(unittest.TestCase):
    def setUp(self):
        self.url = "http://track.atom-data.io/"
        self.data = [{"event_name": "test", "id": "2"}, {"event_name": "2nd", "id": "3"}]
        self.stream = "streamname"
        self.atom_client = api.AtomApi()

    @responses.activate
    def test_perform_call(self):
        responses.add(responses.POST, self.url, json=self.data, status=200)
        self.atom_client.put_events(stream=self.stream, data=self.data)
        self.assertEqual(len(responses.calls), 1, len(responses.calls))

    @responses.activate
    def test_should_receive_data_list(self):
        responses.add(responses.POST, self.url, json=self.data, status=200)
        self.assertRaises(Exception, self.atom_client.put_events, stream=self.stream, data={"event": "name"})

    def test_should_json_dumps_data(self):
        self.atom_client._request_post = MagicMock(return_value=None)
        self.atom_client.put_events(stream=self.stream, data=self.data)

        args, kwargs = self.atom_client._request_post.call_args_list[0]
        data = kwargs['data']

        self.assertIsInstance(data, str, "Should be a string")

        # Check if this is a valid JSON
        json.loads(data)
