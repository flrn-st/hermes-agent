"""Response contracts for ``hermes_cli/memory_oauth.py`` (memory-provider OAuth connect)."""

from __future__ import annotations

from typing import Literal

from hermes_cli.web_responses.base import ResponseModel

MemoryOAuthState = Literal["idle", "pending", "connected", "error"]


class MemoryOAuthStatusResponse(ResponseModel):
    """``memory_oauth_status`` → the provider's ``oauth_flow.get_flow_status()``
    (``plugins/memory/honcho/oauth_flow.py``); ``auth`` names the stored credential, if any."""

    state: MemoryOAuthState
    detail: str
    connected: bool
    auth: Literal["oauth", "apikey"] | None


class MemoryOAuthStartResponse(ResponseModel):
    """``start_memory_oauth`` → ``oauth_flow.start_loopback_flow_background()``: the full status on a
    fresh start, only ``state``/``detail`` when a flow is already pending (idempotent re-click)."""

    state: MemoryOAuthState
    detail: str
    connected: bool | None = None
    auth: Literal["oauth", "apikey"] | None = None
