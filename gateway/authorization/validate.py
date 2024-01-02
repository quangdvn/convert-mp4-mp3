import os

import requests


def token(request):
    if not "Authorization" in request.headers:
        return None, ("Missing Credentials", 401)

    token = request.headers["Authorization"]

    if not token:
        return None, ("Missing Credentials", 401)

    res = requests.post(
        url=f"http://{os.environ.get('AUTH_SERVICE_ADDRESS')}/validate",
        headers={"Authorization": token}
    )

    if res.status_code == 200:
        return res.text, None
    return None, (res.text, res.status_code)
