import json
import random
from ironsource.atom.ironsource_atom import IronSourceAtom
from ironsource.atom.ironsource_atom_tracker import IronSourceAtomTacker

import time

from threading import Thread
from threading import Lock

if __name__ == "__main__":
    api_ = IronSourceAtom()

    api_.enable_debug(True)
    api_.set_endpoint("http://track.atom-data.io/")

    stream = "sdkdev_sdkdev.public.zeev"
    auth_key = "I40iwPPOsG3dfWX30labriCg9HqMfL"

    print ("==== TESTING GET REQUEST TO ATOM ====")
    data_get = {"event_name": "PYTHON_SDK_GET_EXAMPLE", "string_value": str(random.random())}
    response_get = api_.put_event(stream=stream, data=json.dumps(data_get), method="get", auth_key=auth_key)

    print ("GET Response data: " + str(response_get.data) + "; error: " + str(response_get.error) +
           "; status: " + str(response_get.status))

    print ("\n==== TESTING GET REQUEST TO ATOM ====")
    data_post = {"event_name": "PYTHON_SDK_POST_EXAMPLE", "string_value": str(random.random())}
    response_post = api_.put_event(stream=stream, data=json.dumps(data_post), auth_key=auth_key)

    print ("POST Response data: " + str(response_post.data) + "; error: " + str(response_post.error) +
           "; status: " + str(response_post.status))

    print ("\n==== TESTING ATOM TRACKER ====")

    api_tracker = IronSourceAtomTacker()
    # api_tracker.set_bulk_bytes_size(2)
    api_tracker.enable_debug(True)

    api_tracker.set_flush_interval(10)
    api_tracker.set_endpoint("http://track.atom-data.io/")


    class ThreadClass:
        def __init__(self):
            self._call_index = 1
            self._thread_lock = Lock()

        def thread_worker(self, args):
            while True:
                if self._call_index >= 30:
                    return
                with self._thread_lock:
                    data_track = {"id": self._call_index, "event_name": "PYTHON_SDK_TRACKER_EXAMPLE",
                                  "string_value": str(random.random())}
                    self._call_index += 1
                api_tracker.track(stream=stream, data=json.dumps(data_track), auth_key=auth_key)


    t = ThreadClass()
    for index in range(0, 10):
        thread_index = index

        thread = Thread(target=t.thread_worker, args=[thread_index])
        thread.start()

    time.sleep(10)

    api_tracker.stop()
    print ("Finished all example methods.")
