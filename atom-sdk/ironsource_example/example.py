from ironsource.atom.ironsource_atom import IronSourceAtom
from ironsource.atom.ironsource_atom_tracker import IronSourceAtomTacker

import time

from threading import Thread
from threading import Lock

if __name__ == "__main__":
    api_ = IronSourceAtom()

    api_.enable_debug(True);
    api_.set_endpoint("http://track.atom-data.io/");

    stream_get = "sdkdev_sdkdev.public.g8y3etest";
    auth_key = "I40iwPPOsG3dfWX30labriCg9HqMfL";
    data_get = "{\"strings\": \"data GET1111111111111\"}";

    response_get = api_.put_event(stream=stream_get, data=data_get, method="get", auth_key=auth_key);

    print ("Response data: " + str(response_get.data) + "; error: " + str(response_get.error) +
           "; status: " + str(response_get.status))

    api_tracker = IronSourceAtomTacker()
    api_tracker.set_bulk_bytes_size(2)
    api_tracker.enable_debug(True)

    api_tracker.set_flush_interval(2000);
    api_tracker.set_endpoint("http://track.atom-data.io/");

    class ThreadClass:
        def __init__(self):
            self._call_index = 1;
            self._thread_lock = Lock()

        def thread_worker(self, args):
            while True:
                if self._call_index >= 30:
                    return
                stream_track = "sdkdev_sdkdev.public.g8y3etest";
                auth_key_track = "I40iwPPOsG3dfWX30labriCg9HqMfL";
                with self._thread_lock:
                    data_track = "{\"strings\": \"data: " + str(self._call_index) + " aaa t: " + str(args) + "\"}";
                    self._call_index += 1
                api_tracker.track(stream=stream_track, data=data_track, auth_key=auth_key_track)

    t = ThreadClass()
    for index in range(0, 10):
        thread_index = index

        thread = Thread(target=t.thread_worker, args=[thread_index])
        thread.start()

    time.sleep(10)

    api_tracker.stop()
    print ("After track!")