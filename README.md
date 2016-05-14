# ironSource.atom SDK for Python [![License][license-image]][license-url]
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

[license-image]: https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square
[license-url]: LICENSE