"""Primitives for the dashboard REST response contracts.

Routes attach a model with ``responses={200: {"model": X}}``. That is documentation only:
FastAPI renders it into ``/openapi.json`` and never validates, filters or re-serialises what the
handler returns, so a contract cannot change runtime behaviour. ``response_model=`` would. The test
suite holds handlers to their contracts instead (``check.py``).

Modelling rules (the same as ``tui_gateway/contracts/base.py``, so both wires read alike):

- Field names exactly as they travel (most are ``snake_case``; a few routes emit ``camelCase``).
- ``x: X`` = always present. ``x: X | None`` = always present, may be ``null``.
  ``x: X | None = None`` = may be absent (or ``null``). A plain default = may be absent, never ``null``.
- ``ResponseModel`` is ``extra="forbid"``: it lists every key the handler emits.
  ``OpenModel`` is for rows whose closed set is owned elsewhere (state rows, config sections).
- A genuinely open value is ``JsonValue``; ``dict[str, Any]`` is not a contract.
- Each root model's docstring names the producing handler/helper.
- ``defer_build``: the core schemas are only built when ``/openapi.json`` is generated; at import
  the contracts cost class creation plus FastAPI's per-route response field.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict

JsonValue = Any  # a JSON scalar/array/object the contract deliberately leaves open


class ResponseModel(BaseModel):
    model_config = ConfigDict(extra="forbid", defer_build=True)


class OpenModel(ResponseModel):
    """Known fields are typed; the producer may add more."""

    model_config = ResponseModel.model_config | {"extra": "allow"}


class OkResponse(ResponseModel):
    """The bare ``{"ok": true}`` acknowledgement."""

    ok: bool


class ActionSpawnResponse(OkResponse):
    """A backgrounded ``hermes`` action (``_spawn_hermes_action`` / ``spawn_profile_action``); ``name``
    is the log key polled via ``GET /api/actions/{name}/status``."""

    pid: int
    name: str


def binary_body(description: str, *media_types: str) -> dict:
    """``responses=`` entry for raw bytes (a ``FileResponse``) served as any of ``media_types``."""
    return {"description": description,
            "content": {media: {"schema": {"type": "string", "format": "binary"}} for media in media_types}}


def text_body(description: str, media_type: str = "text/html") -> dict:
    """``responses=`` entry for a text document (an ``HTMLResponse`` page, CSS)."""
    return {"description": description, "content": {media_type: {"schema": {"type": "string"}}}}


def redirect(description: str) -> dict:
    """``responses=`` entry for a redirect; ``description`` says where it points."""
    return {"description": description,
            "headers": {"Location": {"description": "Redirect target.", "schema": {"type": "string"}}}}


__all__ = [
    "ActionSpawnResponse", "JsonValue", "OkResponse", "OpenModel", "ResponseModel", "binary_body",
    "redirect", "text_body",
]
