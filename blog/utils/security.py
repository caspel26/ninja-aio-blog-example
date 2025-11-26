import datetime
from joserfc import jwt, jwk
from django.utils import timezone
from django.conf import settings

JWT_PRIVATE: jwk.RSAKey = settings.JWT_PRIVATE


def encode_jwt(
    duration: int, algorithm: str | None = None, token_type: str | None = None , **kwargs
) -> str:
    now = timezone.now()
    nbf = now
    algorithm = algorithm if algorithm else settings.JWT_ALGORITHM
    return jwt.encode(
        header={"alg": algorithm, "typ": "JWT", "kid": JWT_PRIVATE.kid},
        claims={
            "iat": now,
            "nbf": nbf,
            "exp": now + datetime.timedelta(seconds=duration),
            "aud": settings.API_SITE_BASEURL,
            "iss": settings.JWT_COMMON_ISSUER,
        }
        | ({token_type: True} if token_type else {}) | kwargs,
        key=JWT_PRIVATE,
        algorithms=[algorithm if algorithm else settings.JWT_ALGORITHM],
    )
