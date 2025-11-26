from ninja_aio.models import ModelUtil
from ninja_aio.auth import AsyncJwtBearer
from django.conf import settings

from api.models import Author


JWT_PUBLIC = settings.JWT_PUBLIC
ESSENTIAL_CLAIM = {"essential": True}
ALLOW_BLANK_CLAIM = {"allow_blank": True}
AUDIENCES = [settings.API_SITE_BASEURL]  # expected audience values
CLAIMS = {
    "iat": ESSENTIAL_CLAIM,
    "exp": ESSENTIAL_CLAIM,
    "nbf": ESSENTIAL_CLAIM,
    "aud": ESSENTIAL_CLAIM | {"values": AUDIENCES},  # to be verified against expected audience,
    "iss": ESSENTIAL_CLAIM | {"value": settings.JWT_COMMON_ISSUER},  # issuer claim
    "sub": ESSENTIAL_CLAIM,  # subject claim (user identifier)
    "email": ESSENTIAL_CLAIM | ALLOW_BLANK_CLAIM,
    "name": ESSENTIAL_CLAIM | ALLOW_BLANK_CLAIM,
}


class AuthorAuth(AsyncJwtBearer):
    jwt_public = JWT_PUBLIC
    claims = CLAIMS | {"access": ESSENTIAL_CLAIM}
    algorithms = [settings.JWT_ALGORITHM]

    async def auth_handler(self, request):
        try:
            util = ModelUtil(Author)
            request.user = await util.get_object(
                request, getters={"username": self.dcd.claims.get("sub")}
            )
        except Author.DoesNotExist:
            return False
        return request.user


class RefreshAuth(AsyncJwtBearer):
    jwt_public = JWT_PUBLIC
    claims = CLAIMS | {"refresh": ESSENTIAL_CLAIM}
    algorithms = [settings.JWT_ALGORITHM]

    async def auth_handler(self, request):
        try:
            util = ModelUtil(Author)
            request.user = await util.get_object(
                request, getters={"username": self.dcd.claims.get("sub")}
            )
        except Author.DoesNotExist:
            return False
        return request.user