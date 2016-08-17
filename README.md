# ironSource.atom SDK for Python
 [![License][license-image]][license-url]
 [![Docs][docs-image]][docs-url]
 [![Python supported version][python-support]][python-url]
 [![PyPI version][package-image]][package-url]
 [![Build status][travis-image]][travis-url]
 [![Coverage Status][coverage-image]][coverage-url]

atom-python is the official [ironSource.atom](http://www.ironsrc.com/data-flow-management) SDK for the Python programming language.

- [Signup](https://atom.ironsrc.com/#/signup)
- [Documentation](https://ironsource.github.io/atom-python/)
- [Installation](#Installation)
- [Sending an event](#Using-the-API-layer-to-send-events)

## Installation
```bash
$ pip install --upgrade ironsource-atom
```

## Using the IronSource API to send events 
### Tracker usage
Importing the library and initializing
```python
from ironsoure.atom import ironsource_atom_tracker

tracker = ironsource_atom_tracker.IronSourceAtomTacker()

tracker.set_bulk_bytes_size(2048)
tracker.enable_debug(True)

tracker.set_flush_interval(2000)
tracker.set_endpoint("http://track.atom-data.io/")
```
Sending an event - should be a string.
```python 
stream = "<YOUR_STREAM_NAME>"
auth_key = "<YOUR_AUTH_KEY>"
data = "{\"strings\": \"data: test\"}"

tracker.track(stream=stream, data=data, auth_key=auth_key)
```
### Abstract class for store data `EventManager`
Implementation must to be synchronized for multithreading use.
```python
class EventManager:
    """
        Event manager interface for holding data
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        pass

    @abc.abstractmethod
    def add_event(self, event_object):
        """
        Add event (must to be synchronized)

        :param event_object: event data object
        :type event_object: Event
        """
        pass

    @abc.abstractmethod
    def get_event(self):
        """
        Get event (must to be synchronized)

        :return: Event object from storage
        :rtype: Event
        """
        pass

```
Using custom storage implementation:
```python
tracker = new IronSourceAtomTracker();

custom_event_manager = new QueueEventManager();
tracker.set_event_manager(custom_event_manager);
```

### Low level API usage
Importing the library and initializing
```python
from ironsoure.atom import ironsource_atom

api = ironsource_atom.IronSourceAtom()
api.enableDebug(True)

api.set_auth("<YOUR_AUTH_KEY>")
api.set_endpoint("http://track.atom-data.io/")
```
Sending an event - should be a string.
```python
stream = "<YOUR_STREAM_NAME>"
data = "{\"strings\": \"data: test\"}"
api.put_event(stream=stream, data=data, method="post")
```

Sending a bulk of events - should be a list of string.
```python
stream = "<YOUR_STREAM_NAME>"
data = ["{\"strings\": \"data: test 1\"}",
        "{\"strings\": \"data: test 2\"}"]
api.put_events(stream=streams, data=data)
```
### License
MIT

[license-image]: https://img.shields.io/badge/license-MIT-blue.svg
[license-url]: https://github.com/ironSource/atom-python/blob/master/LICENSE
[travis-image]: https://img.shields.io/travis/ironSource/atom-python.svg
[travis-url]: https://travis-ci.org/ironSource/atom-python
[package-image]: https://badge.fury.io/py/ironSourceAtom.svg
[package-url]: https://badge.fury.io/py/ironSourceAtom
[python-support]:  https://img.shields.io/badge/python-2.7%2C%203.3%2C%203.4%2C%203.5-blue.svg
[python-url]: https://www.python.org/
[coverage-image]: https://coveralls.io/repos/github/ironSource/atom-python/badge.svg?branch=master
[coverage-url]: https://coveralls.io/github/ironSource/atom-python?branch=master
[docs-image]: https://img.shields.io/badge/docs-latest-blue.svg
[docs-url]: https://ironsource.github.io/atom-python/