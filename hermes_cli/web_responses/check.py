"""The test suite holds every route to the response contract it documents.

Routers opt in with ``APIRouter(route_class=ContractRoute)`` (``include_router`` keeps the class, so
a router mounted on a test's own ``FastAPI()`` is checked too). Under ``HERMES_TEST_ISOLATION`` —
set by ``tests/conftest.py`` before anything imports a router — every JSON response is validated
against the model its route documents for that status, and a mismatch raises
``ResponseContractViolation``: a handler change that drifts from its contract fails the suite, the
same gate ``tui_gateway/contracts/registry.py`` puts on the JSON-RPC wire. Outside the suite it is a
plain ``APIRoute``: the check gates changes, so the dashboard does not pay for it per request.
"""

from __future__ import annotations

import os
from typing import Any

from fastapi.routing import APIRoute
from pydantic import TypeAdapter, ValidationError
from starlette.responses import Response

_adapters: dict[Any, TypeAdapter] = {}


class ResponseContractViolation(AssertionError):
    """A route answered with a JSON body its documented response model rejects."""


def check_response(route: APIRoute, method: str, response: Response) -> None:
    """Validate a JSON ``response`` against the model ``route`` documents for its status. A 2xx
    JSON body at a status the route documents nothing for is a violation too."""
    body = getattr(response, "body", None)
    if not isinstance(body, (bytes, bytearray)) or "json" not in (response.headers.get("content-type") or ""):
        return  # files, streams, HTML: nothing to validate
    status = response.status_code
    documented = route.responses.get(status) or route.responses.get(str(status))
    where = f"{method} {route.path} -> {status}"
    if documented is None:
        if 200 <= status < 300:
            raise ResponseContractViolation(f"{where}: no response documented for this status")
        return
    model = documented.get("model")
    if model is None:
        return
    adapter = _adapters.get(model) or _adapters.setdefault(model, TypeAdapter(model))
    try:
        adapter.validate_json(body, strict=True)
    except ValidationError as exc:
        raise ResponseContractViolation(f"{where} violates its response contract: {exc}") from exc


class ContractRoute(APIRoute):
    def get_route_handler(self):
        handler = super().get_route_handler()
        if not os.environ.get("HERMES_TEST_ISOLATION"):  # outside the suite: a plain APIRoute
            return handler

        async def checked(request):
            response = await handler(request)
            check_response(self, request.method, response)
            return response

        return checked
