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
$ pip install --upgrade ironSourceAtom
```

### Using the API layer to send events

Importing the library and initializing
```python
from ironSourceAtom import api
client = api.AtomApi(url="http://track.atom-data.io/", auth="<your_auth_key>")
```
Sending an event - should be a string.
```python
stream = "unicorn_startup.analytics"
data = {"user_id": "iron_user", "event_type": "signin"}
client.put_event(stream=stream, data=json.dumps(data), method="post")
```

Sending a bulk of events - should be a list of dicts.
```python
stream = "unicorn_startup.analytics"
data = [{"user_id": "iron_beast", "event_type": "login"},
        {"user_id": "iron_beast", "event_type": "logout"}]
client.put_events(stream=streams, data=data)
```
### License
MIT

[license-image]: https://img.shields.io/badge/license-MIT-blue.svg
[license-url]: https://github.com/ironSource/atom-python/blob/master/LICENSE.txt
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