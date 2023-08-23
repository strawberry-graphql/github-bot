import os

from starlette.datastructures import Headers
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import Receive, Scope, Send
from strawberry.asgi import GraphQL as BaseGraphQL


def is_token_valid(token: str | None) -> bool:
    if os.environ.get("SKIP_TOKEN_CHECK", "false").lower() == "true":
        return True

    if "ALLOWED_TOKEN" not in os.environ:
        message = "ALLOWED_TOKEN env variable not set."

        raise ValueError(message)

    return token == os.environ["ALLOWED_TOKEN"]


def get_token_from_authorization_header(value: str | None) -> str | None:
    if not value:
        return None

    prefix, token = value.split(" ")

    assert prefix == "Bearer"  # noqa: S101

    return token


class GraphQL(BaseGraphQL):
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        request = Request(scope=scope, receive=receive)

        token = self._get_token(scope)

        # Allow GraphiQL
        if request.method != "GET" and not is_token_valid(token):
            response = Response(status_code=403)

            return await response(scope, receive, send)

        await super().__call__(scope=scope, receive=receive, send=send)
        return None

    def _get_token(self, scope: Scope) -> str | None:
        headers = Headers(scope=scope)
        authorization_header = headers.get("Authorization")

        return get_token_from_authorization_header(
            authorization_header,
        )
