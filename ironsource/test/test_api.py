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

from ironsource.atom import ironsource_atom


class TestApiSetterGetter(unittest.TestCase):
    def setUp(self):
        self.url = "http://track.atom-data.io/"
        self.data = {"event_name": "test", "id": "2"}
        self.stream = "streamname"
        self.atom_client = ironsource_atom.IronSourceAtom()

    def test_auth(self):
        expected_auth = "test_auth"
        self.atom_client.set_auth(expected_auth)
        self.assertEqual(self.atom_client.get_auth(), expected_auth)

    def test_endpoint(self):
        expected_endpoint = "test_endpoint"
        self.atom_client.set_endpoint(expected_endpoint)
        self.assertEqual(self.atom_client.get_endpoint(), expected_endpoint)


class TestApiGET(unittest.TestCase):
    def setUp(self):
        self.url = "http://track.atom-data.io/"
        self.data = {"event_name": "test", "id": "2"}
        self.stream = "streamname"
        self.atom_client = ironsource_atom.IronSourceAtom()

    @responses.activate
    def test_api_get_calls(self):
        responses.add(responses.GET, self.url, json=self.data, status=200)
        self.atom_client.put_event(stream=self.stream, data=json.dumps(self.data), method="get", auth_key="test_auth")
        self.assertEqual(len(responses.calls), 1, len(responses.calls))

    @responses.activate
    def test_api_get_response(self):
        responses.add(responses.GET, self.url, json={"Status": "Ok"}, status=200)
        res = self.atom_client.put_event(stream=self.stream, data=json.dumps(self.data), method="get")
        self.assertEqual(res.data, b"{\"Status\": \"Ok\"}")

    @responses.activate
    def test_put_event_post_error(self):
        responses.add(responses.GET, self.url, json={"error": "fail"}, status=501)
        res = self.atom_client.put_event(stream=self.stream, data=json.dumps(self.data), method="get")

        self.assertEqual(res.status, 501)

class TestApiPost(unittest.TestCase):

    def setUp(self):
        self.url = "http://track.atom-data.io/"
        self.data = {"event_name": "test", "id": "2"}
        self.stream = "streamname"
        self.atom_client = ironsource_atom.IronSourceAtom()

    @responses.activate
    def test_api_post_calls(self):
        responses.add(responses.POST, self.url, json=self.data, status=200)
        self.atom_client.put_event(stream=self.stream, data=json.dumps(self.data), auth_key="test_auth")
        self.assertEqual(len(responses.calls), 1, len(responses.calls))

    @responses.activate
    def test_api_post_response(self):
        responses.add(responses.POST, self.url, json={"Status": "Ok"}, status=200)
        res = self.atom_client.put_event(stream=self.stream, data=json.dumps(self.data))
        self.assertEqual(res.data, b"{\"Status\": \"Ok\"}")


class TestPutEvent(unittest.TestCase):
    def setUp(self):
        self.url = "http://track.atom-data.io/"
        self.data = {"event_name": "test", "id": "2"}
        self.stream = "streamname"
        self.atom_client = ironsource_atom.IronSourceAtom()

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

    @responses.activate
    def test_put_event_post_error(self):
        responses.add(responses.POST, self.url, json={"error": "fail"}, status=501)
        res = self.atom_client.put_event(stream=self.stream, data=json.dumps(self.data), method="POST")

        self.assertEqual(res.status, 501)


class TestPutEvents(unittest.TestCase):
    def setUp(self):
        self.url = "http://track.atom-data.io/"
        self.data = [{"event_name": "test", "id": "2"}, {"event_name": "2nd", "id": "3"}]
        self.stream = "streamname"
        self.atom_client = ironsource_atom.IronSourceAtom()

    @responses.activate
    def test_perform_call(self):
        responses.add(responses.POST, self.url, json=self.data, status=200)
        self.atom_client.put_events(stream=self.stream, data=self.data)
        self.assertEqual(len(responses.calls), 1, len(responses.calls))

    @responses.activate
    def test_should_receive_data_list(self):
        responses.add(responses.POST, self.url, json=self.data, status=200)
        self.assertRaises(Exception, self.atom_client.put_events, stream=self.stream, data={"event": "name"})
