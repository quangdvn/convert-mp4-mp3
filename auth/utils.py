import datetime

import jwt


def create_jwt(username: str, secret: str, authz: bool) -> str:
    now = datetime.datetime.utcnow()
    now_with_tz = now.replace(tzinfo=datetime.timezone.utc)
    exp_time = now_with_tz + datetime.timedelta(days=1)

    return jwt.encode(
        {
            "username": username,
            "exp": exp_time,
            "iat": now_with_tz,
            "admin": authz
        },
        secret,
        # Symmetric encryption algorithm, advanced is RS256 (Asymmetric algorithm)
        algorithm="HS256"
    )
