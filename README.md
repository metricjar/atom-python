# ironSource.atom SDK for Python

[![License][license-image]][license-url]
[![Docs][docs-image]][docs-url]
[![Build status][travis-image]][travis-url]
[![Coverage Status][coverage-image]][coverage-url]
[![Python supported version][python-support]][python-url]
[![PyPI version][package-image]][package-url]
 
atom-python is the official [ironSource.atom](http://www.ironsrc.com/data-flow-management) SDK for Python

- [Signup](https://atom.ironsrc.com/#/signup)
- [Documentation][docs-url]
- [Installation](#installation)
- [Usage](#usage)
- [Change Log](#change-log)
- [Example](#example)

## Installation

### Installing with pip:
```bash
$ pip install --upgrade ironsource-atom
```

## Usage

You may use the SDK in two different ways:

1. High level "Tracker" - contains in-memory storage and tracks events based on certain parameters.
2. Low level - contains 2 methods: putEvent() and putEvents() to send 1 event or a batch respectively.

### High Level SDK - "Tracker"
**NOTE:**
The tracker is a based on a thread pool which is controlled by BatchEventPool and a backlog (QueueEventStorage)
By default the BatchEventPool is configured to use one thread (worker), you can change it when constructing the tracker.  
These are the default parameters for both Classes (inside config.py):

```python
# Tracker Config
BATCH_SIZE = 256
BATCH_SIZE_LIMIT = 2000
BATCH_BYTES_SIZE = 64 * 1024
BATCH_BYTES_SIZE_LIMIT = 512 * 1024
# Default flush interval in milliseconds
FLUSH_INTERVAL = 10000

# Batch Event Pool Config
# Default Number of workers(threads) for BatchEventPool
BATCH_WORKER_COUNT = 1
# Default Number of batch events to hold in BatchEventPool
BATCH_POOL_SIZE = 1

# EventStorage Config (backlog)
# Default backlog queue size (per stream)
BACKLOG_SIZE = 500

# Retry on 500 / Connection error conf
# Retry max time in seconds
RETRY_MAX_TIME = 1800
# Maximum number of retries (set it to 1 in order to disable retry). This value is ignored if RETRY_FOREVER = True
RETRY_MAX_COUNT = 12
# Base multiplier for exponential backoff calculation
RETRY_EXPO_BACKOFF_BASE = 3
# Should the worker in BatchEventPool retry forever on server error (recommended)
RETRY_FOREVER = True

# Tracker backlog conf
# Tracker backlog Queue GET & PUT Block or not.
BACKLOG_BLOCKING = True
# Tracker backlog Queue GET & PUT timeout in seconds (ignored if backlog is blocking)
BACKLOG_TIMEOUT = 1

# HTTP requests lib session GET/POST timeout in seconds (default: 60 seconds)
REQUEST_TIMEOUT = 60

# Debug file path once debug_to_file is enabled
DEBUG_FILE_PATH = "/tmp/"

# Init a new tracker:
tracker = IronSourceAtomTracker(batch_worker_count=config.BATCH_WORKER_COUNT,
                                batch_pool_size=config.BATCH_POOL_SIZE,
                                event_backlog=None,
                                backlog_size=config.BACKLOG_SIZE,
                                flush_interval=config.FLUSH_INTERVAL,
                                retry_max_time=config.RETRY_MAX_TIME,
                                retry_max_count=config.RETRY_MAX_COUNT,
                                batch_size=config.BATCH_SIZE,
                                batch_bytes_size=config.BATCH_BYTES_SIZE,
                                is_debug=False,
                                debug_to_file=False,
                                debug_file_path=config.DEBUG_FILE_PATH,
                                endpoint=config.ATOM_ENDPOINT,
                                auth_key="",
                                callback=None,
                                retry_forever=config.RETRY_FOREVER,
                                is_blocking=config.BACKLOG_BLOCKING,
                                backlog_timeout=config.BACKLOG_TIMEOUT,
                                request_timeout=config.REQUEST_TIMEOUT)
"""
:param batch_worker_count: Optional, Number of workers(threads) for BatchEventPool
:param batch_pool_size:    Optional, Number of events to hold in BatchEventPool
:param event_backlog:      Optional, Custom EventStorage implementation
:param backlog_size:       Optional, Backlog queue size (EventStorage ABC implementation)
:param flush_interval:     Optional, Tracker flush interval in milliseconds (default 10000)
:param retry_max_time:     Optional, Retry max time in seconds
:param retry_max_count:    Optional, Maximum number of retries in seconds
:param batch_size:         Optional, Amount of events in every batch (bulk) (default: 256)
:param batch_bytes_size:   Optional, Size of each batch (bulk) in bytes (default: 64KB)
:param is_debug:           Optional, Enable printing of debug information
:param debug_to_file:      Optional, Should the Tracker write the request and response objects to file
:param debug_file_path:    Optional, the path to the debug file (debug_to_file must be True) (default: /tmp)
:param endpoint:           Optional, Atom endpoint
:param auth_key:           Optional, Default auth key to use (when none is provided in .track)
:param callback:           Optional, callback to be called on error (Client 400/ Server 500)
:param retry_forever:      Optional, should the BatchEventPool retry forever on server error (default: True)
:param is_blocking:        Optional, should the tracker backlog block (default: True)
:param backlog_timeout:    Optional, tracker backlog block timeout (ignored if is_blocking, default: 1 second)
:param request_timeout:    Optional, HTTP requests lib session GET/POST timeout in seconds (default: 60 seconds)

The callback convention is: callback(unix_time, http_code, error_msg, sent_data, stream_name)
error_msg = Sdk/server error msg
"""
```

Importing the library and initializing  
```python
from ironsource.atom.ironsource_atom_tracker import IronSourceAtomTracker

# Note the parameters as described above
tracker = IronSourceAtomTracker(batch_bytes_size=2048, batch_size=12, flush_interval=2000)
tracker.set_debug(True) # Optional, Print debug information (You can also set it at the constructor)

# Sending an event
stream = "YOUR_STREAM_NAME"
auth_key = "YOUR_HMAC_AUTH_KEY"

# Example of an event
data = {"id": 123, "event_name": "PYTHON_SDK_TRACKER_EXAMPLE"}
tracker.track(stream=stream, data=data, auth_key=auth_key) # auth_key is optional

# To force flush all events, use:
tracker.flush()

# To stop the tracker, use:
tracker.stop()
```
### Logging of request/response to file (since version 1.5.4)
**Note:** this is recommended only if you want to debug the SDK  
To enable use: `debug_to_file` parameter at the tracker construction  
To specify path use: `debug_file_path` (defaults to /tmp/)  
The logging will produce JSON files with request and response objects.  
Each request-response pair will have a unique id.  
Logging file name is: atom-raw.{month}-{day}.json  
The file will log-rotate at 50MB and save up to 100 files, based on: RotatingFileHandler at Python Logging module.

### Abstract class for storing data at tracker backlog `EventStorage`
If you'd like to customize the tracker backlog, implement the following abstract class.
Implementation must to be synchronized for multi threading use.
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
    def get_event(self, stream):
        """
        Get event (must to be synchronized)

        :return: Event object from storage
        :rtype: Event
        """
        pass

    @abc.abstractmethod
    def remove_event(self, stream):
        """
        Remove event from storage
        :param stream:
        :return: None
        """
        pass

    @abc.abstractmethod
    def is_empty(self):
        """
        Check if the storage is empty
        :return: True is empty, else False
        """
        pass


# Using custom storage implementation:

custom_event_storage_backlog = MyCustomEventStorage()
tracker = IronSourceAtomTracker(event_backlog=custom_event_storage_backlog)
```

### Low Level (Basic) SDK

The Low Level SDK has 2 methods:  
- putEvent - Sends a single event to Atom.
- putEvents - Sends a bulk (batch) of events to Atom.

```python
from ironsource.atom.ironsource_atom import IronSourceAtom

auth = "DEFAULT_AUTH_KEY"
api = IronSourceAtom(is_debug=False, endpoint=config.ATOM_ENDPOINT, auth_key="", request_timeout=60,
                     debug_to_file=False, debug_file_path=config.DEBUG_FILE_PATH)
"""
Atom class init function
:param is_debug:            Optional, Enable/Disable debug
:param endpoint:            Optional, Atom API Endpoint
:param auth_key:            Optional, Atom auth key
:param request_timeout:     Optional, request timeout (default: 60)
:param debug_to_file:       Optional, Should the Tracker write the request and response objects to file (default: False)
:param debug_file_path:     Optional, the path to the debug file (debug_to_file must be True) (default: /tmp)
"""
# Note: If you don't specify an auth key, then it would use the default (if you set it with set_auth)
# Else it won't use any.

# Sending an event - should be a string.
stream = "YOUR_STREAM_NAME"
auth2 = "YOUR_AUTH_KEY"
data = {"event_name": "PYTHON_SDK_POST_EXAMPLE"}
api.put_event(stream=stream, data=data, method="post", auth_key=auth2) # Will send with auth2
api.put_event(stream=stream, data=data) # Will send with auth

# Sending a bulk of events - should be a list of strings.
stream = "YOUR_STREAM_NAME"
data = [{"strings": "data: test 1"}, {"strings": "data: test 2"}]
api.put_events(stream=stream, data=data, auth_key=auth2)
```

## Change Log

### v1.5.4
- Added support for logging of all requests and responses to file
- BugFix: Graceful shutdown did not stop the tracker completely while there are requests in flight and server-error.
- Added raw 'requests' lib response to the Response class.
- Added top limits to tracker conf

### v1.5.3
- Added timeout to GET and POST (default 60 seconds)

### v1.5.2
- Added retry_forever option for tracker (default now)
- Added an option to set the tracker backlog queue as non-blocking

### v1.5.1
- Tracker changes:
    - BugFix: replaced dequeue with Queue.Queue on Backlog & BatchEventPool.  
      dequeue caused excessive consumption of memory and cpu.  
      Note that .track() is now blocking when backlog is full
    - Changed defaults for Backlog & BatchEventPool
    - bug fix: fixing a case of negative timer when executing after sleep
    - bug fix: fixing a bug in the tracker handler when there are no tracked events (busy waiting)
    
### v1.5.0
- Tracker changes:
    - Added periodical flush function and changed the interval mechanism
	- Changed the flush all streams (flush_all) mechanism
	- Added max retry (enqueue again after reached)
	- Improved graceful shutdown and signal catching
	- Added more options to the constructor and removed logger from tracker
    - Added more verbose logging
	- Added callback function to tracker (optional callback on error)
	- Added Exponential backoff with full jitter
	- Renamed enable_debug -> set_debug (also on Atom class)
	- Removed the following (moved them to the constructor):
	    - set_bulk_size
	    - set_bulk_byte_size
	    - set_endpoint
	    - set_flush_interval
    - Improved error handling and input checking
- BatchEventPool - Added is_empty() func
- Changed logger (added logger.py)
- Added config.py for constants
- EventStorage and QueueEventStorage - Added is_empty() func
- Requests class - Improved HTTP class, changed error handling and removed useless code
- Atom Class:
    - Improved error handling and input checking
    - Removed the following (moved them to the constructor):
        - get_endpoint()
        - set_endpoint()
        - set_auth()
- Updated Docs


### v1.1.7
- Added deque limit on QueueEventStorage(backlog)
- Updated example
- Changed defaults on BatchEventPool and QueueEventStorage
- Changed all pop() from deque to popleft()

### v1.1.6
- Fixed a bug in python3 compatibility

### v1.1.5
- Updated Docs
- Updated README
- Added support for sending data without json.dumps
- Added Graceful shutdown
- Fixed a bug in retry mechanism
- Updated example

### v1.1.2
- High Level API - Tracker
- Tracker Class with thread support
- EventStorage ABC
- Changing python package to match python convention
- Upadting readme
- Fixing auth mechanism

### v1.0.2
- Added support to send a bulk(batch) of events via the put_events method

### v1.0.1
- Added Docs

### v1.0.0
- Basic feature - putEvent

## Example

You can use our [example][example-url] for sending data to Atom

## License
[MIT][license-url]

[example-url]: ironsource_example/
[license-image]: https://img.shields.io/badge/license-MIT-blue.svg
[license-url]: LICENSE
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
