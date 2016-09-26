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
- [Installation](#installation)
- [Usage](#usage)
- [Example](#example)

## Installation
Installing with pip:
```bash
$ pip install --upgrade ironsource-atom
```

## Usage
 
### Tracker usage
Importing the library and initializing

```python
import json
from ironsource.atom.ironsource_atom_tracker import IronSourceAtomTracker

tracker = IronSourceAtomTracker()
tracker.set_bulk_bytes_size(2048) # Optional, Size of each bulk in bytes (default: 64KB)
tracker.set_bulk_size(12) # Optional, Number of events per bulk (batch) (default: 500) 
tracker.set_flush_interval(2000) # Optional, Tracker flush interval in milliseconds (default: 10 seconds)
tracker.enable_debug(True) # Optional, print debug information
tracker.set_endpoint("http://track.atom-data.io/") # Optional, Atom endpoint

# Sending an event
stream = "YOUR_STREAM_NAME"
auth_key = "YOUR_HMAC_AUTH_KEY"

# Example of an event
data = {"id": 123, "event_name": "PYTHON_SDK_TRACKER_EXAMPLE"}
tracker.track(stream=stream, data=json.dumps(data), auth_key=auth_key) # auth_key is optional

# To force flush all events, use:
tracker.flush()
```
### Abstract class for store data `EventStorage`
Implementation must to be synchronized for multithreading use.
```python
import abc

class EventStorage:
    """
        Abstract Base Class for providing a generic way of storing events in a backlog before they are sent to Atom.
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

# Using custom storage implementation:
tracker = new IronSourceAtomTracker();

custom_event_manager = new QueueEventStorage();
tracker.set_event_manager(custom_event_manager);
```

### Low level API usage
Importing the library and initializing
```python
from ironsource.atom.ironsource_atom import IronSourceAtom

api = IronSourceAtom()
api.enable_debug(True)
api.set_auth("YOUR_AUTH_KEY")
api.set_endpoint("http://track.atom-data.io/")
# Sending an event - should be a string.

stream = "<YOUR_STREAM_NAME>"
data = {"event_name": "PYTHON_SDK_POST_EXAMPLE"}
api.put_event(stream=stream, data=json.dumps(data), method="post")

# Sending a bulk of events - should be a list of strings.

stream = "YOUR_STREAM_NAME"
data = [{"strings": "data: test 1"}, {"strings": "data: test 2"}]
api.put_events(stream=stream, data=data)
```

## Example

You can use our [example][example-url] for sending data to Atom

## License
[MIT][license-url]

[license-image]: https://img.shields.io/badge/license-MIT-blue.svg
[license-url]: LICENSE
[example-url]: atom-sdk/ironsource_example/
[travis-image]: https://img.shields.io/travis/ironSource/atom-python.svg
[travis-url]: https://travis-ci.org/ironSource/atom-python
[package-image]: https://badge.fury.io/py/ironsource-atom.svg
[package-url]: https://badge.fury.io/py/ironsource-atom
[python-support]:  https://img.shields.io/badge/python-2.7%2C%203.3%2C%203.4%2C%203.5-blue.svg
[python-url]: https://www.python.org/
[coverage-image]: https://coveralls.io/repos/github/ironSource/atom-python/badge.svg?branch=master
[coverage-url]: https://coveralls.io/github/ironSource/atom-python?branch=master
[docs-image]: https://img.shields.io/badge/docs-latest-blue.svg
[docs-url]: https://ironsource.github.io/atom-python/