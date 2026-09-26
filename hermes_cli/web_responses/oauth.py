"""Response contracts for ``hermes_cli/web_routers/oauth.py``."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from hermes_cli.web_responses.base import ResponseModel


class OAuthProviderStatus(ResponseModel):
    """``_resolve_provider_status`` — the union of ``_status_card`` (plus the Nous tier fields),
    the catalog ``status_fn`` cards in ``hermes_cli/web_server_oauth.py`` (``configured`` is
    copilot-acp only; a logged-out Anthropic/Claude Code card is just ``logged_in`` + ``source``),
    and the ``{"logged_in": false, "error"}`` fallback when a status helper raised."""

    logged_in: bool
    source: str | None = None
    source_label: str | None = None
    token_preview: str | None = Field(default=None, description="Last few characters only, never the token.")
    expires_at: str | float | None = Field(
        default=None, description="As the provider stores it: an ISO timestamp or an epoch number (Claude Code: ms).")
    has_refresh_token: bool | None = None
    last_refresh: str | None = None
    free_tier: bool | None = None
    account_tier: str | None = None
    configured: bool | None = None
    error: str | None = None


class OAuthProviderRow(ResponseModel):
    """One ``_build_oauth_catalog`` row; ``disconnectable`` is ``disconnect_hint is None``."""

    id: str
    name: str
    flow: str = Field(description='Catalog flow: "device_code" or "external" for the built-in cards.')
    cli_command: str
    docs_url: str
    disconnect_hint: str | None
    disconnect_command: str | None
    disconnectable: bool
    status: OAuthProviderStatus


class OAuthProviderListResponse(ResponseModel):
    """``list_oauth_providers``."""

    providers: list[OAuthProviderRow]


class OAuthDisconnectResponse(ResponseModel):
    """``disconnect_oauth_provider``; ``ok`` is whether any credential was actually cleared."""

    ok: bool
    provider: str


class OAuthDeviceCodeStartResponse(ResponseModel):
    """``start_oauth_login`` — the per-provider ``_start_*_device_code`` display fields."""

    session_id: str
    flow: Literal["device_code"]
    user_code: str
    verification_url: str
    expires_in: int
    poll_interval: int


class OAuthSessionPollResponse(ResponseModel):
    """``poll_oauth_session``. ``reason`` / ``account_email`` / ``model`` / ``retryable`` /
    ``retry_after`` are only set by a Nous sign-in over a free-tier identity
    (``hermes_cli/web_server_oauth.py::_record_sign_in_state``)."""

    session_id: str
    status: Literal["pending", "approved", "denied", "expired", "error", "cancelled"]
    error_message: str | None
    expires_at: float | None = Field(description="Epoch seconds; null until the flow knows it.")
    reason: str | None
    account_email: str | None
    model: str | None
    retryable: bool | None
    retry_after: int | None


class OAuthSessionCancelResponse(ResponseModel):
    """``cancel_oauth_session``: ``{"ok": true, "session_id"}`` or, for an unknown session,
    ``{"ok": false, "message"}``."""

    ok: bool
    session_id: str | None = None
    message: str | None = None
