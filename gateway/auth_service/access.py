import os

import requests


def login(request):
    auth = request.authorization
    if not auth:
        return None, ("Missing Credentials", 401)
    basic_auth = (auth.username, auth.password)

    res = requests.post(
        url=f"http://{os.environ.get('AUTH_SERVICE_ADDRESS')}/login",
        auth=basic_auth
    )
    print("Receive: ", res)
    if res.status_code == 200:
        return res.text, None

    return None, (res.text, res.status_code)
