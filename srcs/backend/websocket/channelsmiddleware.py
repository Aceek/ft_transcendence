import django

django.setup()
from channels.db import database_sync_to_async
from authentication.authentication import CookieJWTAuthentication
from django.contrib.auth.models import AnonymousUser


@database_sync_to_async
def get_user_from_jwt(token):
    jwt_auth = CookieJWTAuthentication()
    validated_token = jwt_auth.get_validated_token(token)
    return jwt_auth.get_user(validated_token)


class JwtAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    def __call__(self, scope, receive, send):
        return JwtAuthMiddlewareInstance(scope, self)(receive, send)


class JwtAuthMiddlewareInstance:
    def __init__(self, scope, middleware):
        self.scope = scope
        self.inner = middleware.inner

    async def __call__(self, receive, send):
        raw_token = None
        headers = dict(self.scope["headers"])
        cookies = headers.get(b"cookie", b"").decode("utf-8")
        for cookie in cookies.split("; "):
            if cookie.startswith("access_token="):
                raw_token = cookie.split("=")[1]
                break

        if raw_token:
            try:
                user = await get_user_from_jwt(raw_token)
                self.scope["user"] = user
            except Exception as e:
                self.scope["user"] = AnonymousUser()
        else:
            self.scope["user"] = AnonymousUser()

        return await self.inner(self.scope, receive, send)


def JwtAuthMiddlewareStack(inner):
    return JwtAuthMiddleware(inner)
