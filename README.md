# ironSource.atom SDK for Python
 [![License][license-image]][license-url]
 [![Build status][travis-image]][travis-url]
  [![Python supported version][python-support]][python-url]
 [![PyPI version][package-image]][package-url]
 [![Coverage Status][coverage-image]][coverage-url]

atom-python is the official [ironSource.atom](http://www.ironsrc.com/data-flow-management) SDK for the Python programming language.

- [Signup](https://atom.ironsrc.com/#/signup)
- [Installation](#Installation)
- [Sending an event](#Using-the-API-layer-to-send-events)

#### Installation
```sh
$ pip install --upgrade ironSourceAtom
```

#### Using the API layer to send events

Here's an example of sending an event:
```python
import json
from ironSourceAtom import api

client = api.AtomApi(url="http://track.atom-data.io/", auth="<your_auth_key>")
stream = "unicorn_startup.analytics"
data = {"user_id": "iron_user", "event_type": "signin"}
client.put_event(stream=stream, data=json.dumps(data), method="post")
```



### License
MIT

[license-image]: https://img.shields.io/badge/license-MIT-blue.svg
[license-url]: https://github.com/ironSource/atom-python/blob/master/LICENSE.txt
[travis-image]: https://img.shields.io/travis/ironSource/atom-python.svg
[travis-url]: https://travis-ci.org/ironSource/atom-python.svg?branch=master
[package-image]: https://badge.fury.io/py/ironSourceAtom.svg
[package-url]: https://badge.fury.io/py/ironSourceAtom
[python-support]:  https://img.shields.io/badge/python-2.7%2C%203.3%2C%203.4%2C%203.5-blue.svg
[python-url]: https://www.python.org/
[coverage-image]: https://coveralls.io/repos/github/ironSource/atom-python/badge.svg?branch=master
[coverage-url]: https://coveralls.io/github/ironSource/atom-python?branch=master