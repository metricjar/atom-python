from ironsource.atom.ironsource_atom import IronSourceAtom

if __name__ == "__main__":
    api = IronSourceAtom()

    auth_key = "I40iwPPOsG3dfWX30labriCg9HqMfL"
    api.set_auth(auth_key=auth_key)

    stream_name = "sdkdev_sdkdev.public.g8y3etest"
    data_str = "{\"strings\": \"test data 1\"}"

    api.set_endpoint("http://track.atom-data.io/")

    response = api.put_event(stream=stream_name, data=data_str, method="get")

    print "Response data: " + response.data + "; error: " + response.error + "; status:" + response.status

