import json
import random
from ironsource.atom.ironsource_atom import IronSourceAtom
from ironsource.atom.ironsource_atom_tracker import IronSourceAtomTracker

import time

from threading import Thread
from threading import Lock

if __name__ == "__main__":
    stream = "sdkdev_sdkdev.public.zeev"
    auth_key = "I40iwPPOsG3dfWX30labriCg9HqMfL"

    api_ = IronSourceAtom(is_debug=True)
    api_.enable_debug(True)
    api_.set_endpoint("https://track.atom-data.io/")

    # put_event() GET example
    print ("==== GET REQUEST TO ATOM WITH JSON DUMPS ====")
    data_get = {"id": 1, "event_name": "PYTHON_SDK_GET_EXAMPLE_STRING", "string_value": str(random.random())}
    response_get = api_.put_event(stream=stream, data=json.dumps(data_get), method="get", auth_key=auth_key)
    print ("GET Response data: " + str(response_get.data) + "; error: " + str(response_get.error) +
           "; status: " + str(response_get.status))

    print ("\n==== GET REQUEST TO ATOM WITH DICT ====")
    data_get = {"id": 2, "event_name": "PYTHON_SDK_GET_EXAMPLE_DICT", "string_value": str(random.random())}
    response_get = api_.put_event(stream=stream, data=data_get, method="get", auth_key=auth_key)
    print ("GET Response data: " + str(response_get.data) + "; error: " + str(response_get.error) +
           "; status: " + str(response_get.status))

    # put_event() POST example
    print ("\n==== POST REQUEST TO ATOM WITH JSON DUMPS ====")
    data_post = {"id": 3, "event_name": "PYTHON_SDK_POST_EXAMPLE_STRING", "string_value": str(random.random())}
    response_post = api_.put_event(stream=stream, data=json.dumps(data_post), auth_key=auth_key)
    print ("POST Response data: " + str(response_post.data) + "; error: " + str(response_post.error) +
           "; status: " + str(response_post.status))

    print ("\n==== POST REQUEST TO ATOM WITH DICT ====")
    data_post = {"id": 4, "event_name": "PYTHON_SDK_POST_EXAMPLE_DICT", "string_value": str(random.random())}
    response_post = api_.put_event(stream=stream, data=data_post, auth_key=auth_key)
    print ("POST Response data: " + str(response_post.data) + "; error: " + str(response_post.error) +
           "; status: " + str(response_post.status))

    # put_events example
    print ("\n==== BATCH POST REQUEST TO ATOM ====")
    data_post = [{"id": 5, "event_name": "PYTHON_SDK_BATCH_POST_EXAMPLE", "string_value": str(random.random())},
                 {"id": 6, "event_name": "PYTHON_SDK_BATCH_POST_EXAMPLE", "string_value": str(random.random())}]
    response_post = api_.put_events(stream=stream, data=data_post, auth_key=auth_key)
    print ("POST Response data: " + str(response_post.data) + "; error: " + str(response_post.error) +
           "; status: " + str(response_post.status))

    # tracker example
    print ("\n==== TESTING ATOM TRACKER ====")

    # Tracker callback function example
    def callback_func(timestmap, status, msg, data):
        print("[EXAMPLE CALLBACK FUNCTION] timestamp: {}, status: {} message: {}".format(timestmap, status, msg))

    api_tracker = IronSourceAtomTracker(flush_interval=2000, callback=callback_func)
    api_tracker.set_batch_bytes_size(64000)
    api_tracker.set_batch_size(100)
    # The flush interval is set twice in order to see the change while it's running
    api_tracker.set_flush_interval(10000)
    api_tracker.enable_debug(True)
    api_tracker.set_endpoint("http://track.atom-data.io/")
    # api_tracker.set_endpoint("http://127.0.0.1:3000/")


    class ThreadClass:
        def __init__(self):
            self._call_index = 0
            self._thread_lock = Lock()

        def thread_worker(self, args):

            while True:
                with self._thread_lock:
                    self._call_index += 1
                    data_track = {"id": self._call_index, "event_name": "PYTHON_SDK_TRACKER_EXAMPLE",
                                  "string_value": str(random.random())}
                    # exit after 40
                    if self._call_index >= 100:
                        return
                    else:
                        # Track every odd event with delay
                        if self._call_index % 10 == 0:
                            time.sleep(3)
                            print("[EXAMPLE] Tracking Data")
                    api_tracker.track(stream=stream, data=data_track, auth_key=auth_key)


    threads_array = []
    thread_instance = ThreadClass()
    for index in range(0, 10):
        thread_index = index
        thread = Thread(target=thread_instance.thread_worker, args=[thread_index])
        threads_array.append(thread)

    for thread in threads_array:
        thread.start()

    for thread in threads_array:
        thread.join()

    time.sleep(10000)
    print ("Finished all example methods.")
