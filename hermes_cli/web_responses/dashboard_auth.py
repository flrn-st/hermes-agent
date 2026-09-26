"""Response contracts for ``hermes_cli/dashboard_auth/routes.py``.

Identity fields mirror ``hermes_cli/dashboard_auth/base.py::Session`` (all mandatory strings;
providers without a value send ``""``; ``expires_at`` is the access token's ``exp`` in unix
seconds).
"""

from __future__ import annotations

from typing import Literal

from hermes_cli.web_responses.base import ResponseModel, redirect, text_body

DASHBOARD_AUTH_LOGIN_PAGE_RESPONSES = {200: text_body("The server-rendered login page (``no-store``).")}
DASHBOARD_AUTH_LOGIN_REDIRECT_RESPONSES = {302: redirect(
    "Password providers: to the ``/login`` form (``next`` preserved); otherwise to the IDP's "
    "authorize URL with the PKCE cookie set.")}
DASHBOARD_AUTH_NATIVE_AUTHORIZE_RESPONSES = {
    200: text_body("Provider chooser page, when ``provider`` is empty and several interactive "
                   "providers are registered (``no-store``)."),
    302: redirect("Password providers: to the ``/login`` form; otherwise to the IDP's authorize URL. "
                  "Both set the PKCE cookie carrying the native broker handle."),
}
DASHBOARD_AUTH_CALLBACK_RESPONSES = {302: redirect(
    "Browser login: to the validated ``next`` path (or ``/``) with the session cookies set. Native "
    "login: to the desktop's loopback ``redirect_uri?code=…&state=…``, no session cookies.")}
DASHBOARD_AUTH_LOGOUT_RESPONSES = {302: redirect("To ``/login`` with the session and PKCE cookies cleared.")}


class DashboardAuthProviderOption(ResponseModel):
    name: str
    display_name: str
    supports_password: bool


class DashboardAuthProvidersResponse(ResponseModel):
    """``api_auth_providers``: the interactive (session) providers, the login page's options."""

    providers: list[DashboardAuthProviderOption]


class DashboardAuthNoProvidersResponse(ResponseModel):
    """``api_auth_providers`` 503 when no interactive provider is registered (fail closed)."""

    detail: str


class DashboardAuthPasswordLoginResponse(ResponseModel):
    """``auth_password_login``: ``next`` is the validated landing path (session cookies set), or
    the desktop's loopback redirect URL on a native sign-in (no cookies)."""

    ok: bool
    next: str


class DashboardAuthBearerTokenResponse(ResponseModel):
    """``_bearer_payload`` (``auth_native_token``, ``auth_native_refresh``): tokens in the body,
    no cookie."""

    access_token: str
    refresh_token: str
    token_type: Literal["Bearer"]
    expires_at: int
    provider: str
    user_id: str


class DashboardAuthSessionExpiredResponse(ResponseModel):
    """``auth_native_refresh`` 401 when every provider rejects the refresh token; the desktop
    restarts sign-in."""

    error: Literal["session_expired"]
    detail: str


class DashboardAuthMeResponse(ResponseModel):
    """``api_auth_me``: the verified ``request.state.session`` minus its tokens. With the auth gate
    off it reports the loopback identity instead (``user_id: "local"``, ``provider: "loopback"``,
    ``expires_at: 0``)."""

    user_id: str
    email: str
    display_name: str
    org_id: str
    provider: str
    expires_at: int


class DashboardAuthWsTicketResponse(ResponseModel):
    """``api_auth_ws_ticket``: a single-use WS upgrade ticket (``ws_tickets.TTL_SECONDS``)."""

    ticket: str
    ttl_seconds: int
