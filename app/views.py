import os
from typing import Optional

from starlette.datastructures import Headers
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import Receive, Scope, Send
from strawberry.asgi import GraphQL as BaseGraphQL


def is_token_valid(token: str) -> bool:
    return token == os.environ["ALLOWED_TOKEN"]


def get_token_from_authorization_header(value: Optional[str]) -> Optional[str]:
    if not value:
        return None

    prefix, token = value.split(" ")

    assert prefix == "Bearer"

    return token


class GraphQL(BaseGraphQL):
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        request = Request(scope=scope, receive=receive)

        token = self._get_token(scope)

        # Allow GraphiQL
        if request.method != "GET":
            if token is None:
                response = Response(status_code=401)

                return await response(scope, receive, send)

            if not is_token_valid(token):
                response = Response(status_code=403)

                return await response(scope, receive, send)

        await super().__call__(scope=scope, receive=receive, send=send)

    def _get_token(self, scope: Scope) -> Optional[str]:
        headers = Headers(scope=scope)
        authorization_header = headers.get("Authorization")

        return get_token_from_authorization_header(
            authorization_header,
        )
