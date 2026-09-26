"""Response contracts for ``hermes_cli/web_routers/messaging.py``."""

from __future__ import annotations

from typing import Literal

from hermes_cli.web_responses.base import OpenModel, ResponseModel


class WhatsAppOnboardingResponse(ResponseModel):
    """``hermes_cli/web_server_messaging.py::_whatsapp_onboarding_payload`` — the
    ``_WhatsAppOnboardingSession`` fields in ``_WHATSAPP_PAYLOAD_FIELDS``."""

    pairing_id: str
    status: Literal["starting", "installing", "waiting", "connected", "error", "expired", "cancelled"]
    qr_payload: str | None
    expires_at: str
    mode: Literal["bot", "self-chat"]
    allowed_users: str
    account_id: str | None
    account_name: str | None
    account_phone: str | None
    error: str | None


class MessagingOnboardingApplyResult(ResponseModel):
    """``needs_restart`` + ``hermes_cli/web_server_gateway.py::_restart_gateway_after``: a spawned
    restart carries ``restart_action``/``restart_pid``, a failed one ``restart_error``."""

    ok: bool
    needs_restart: bool
    restart_started: bool
    restart_action: Literal["gateway-restart"] | None = None
    restart_pid: int | None = None
    restart_error: str | None = None


class WhatsAppOnboardingApplyResponse(MessagingOnboardingApplyResult):
    """``apply_whatsapp_onboarding``."""

    platform: Literal["whatsapp"]


class TelegramOnboardingStartResponse(ResponseModel):
    """``start_telegram_onboarding`` — the setup service's pairing, trimmed to strings."""

    pairing_id: str
    suggested_username: str
    deep_link: str
    qr_payload: str
    expires_at: str


class TelegramOnboardingStatusResponse(ResponseModel):
    """``get_telegram_onboarding_status``: ``waiting`` carries only ``expires_at``;
    ``ready`` is ``_telegram_ready_payload``. Terminal statuses are 410s."""

    status: Literal["waiting", "ready"]
    expires_at: str
    bot_username: str | None = None
    owner_user_id: str | None = None


class TelegramOnboardingApplyResponse(MessagingOnboardingApplyResult):
    """``apply_telegram_onboarding``."""

    platform: Literal["telegram"]
    bot_username: str | None


class MessagingPlatformEnvVar(ResponseModel):
    """One ``env_vars`` row of ``_messaging_platform_payload`` (``_messaging_env_info`` prose).
    ``is_list`` marks an allowlist key (comma-separated IDs, never a password): only those carry
    the saved ``value``, which is ``null`` on every other row."""

    key: str
    required: bool
    is_set: bool
    redacted_value: str | None
    value: str | None
    description: str
    prompt: str
    help: str
    url: str | None
    is_password: bool
    is_list: bool
    advanced: bool


class MessagingHomeChannel(OpenModel):
    """``gateway/config.py::HomeChannel.to_dict``; profile-scoped reads pass the config.yaml
    ``platforms.<id>.home_channel`` mapping through as written."""

    platform: str | None = None
    chat_id: str | None = None
    name: str | None = None
    thread_id: str | None = None
    user_id: str | None = None
    scope_id: str | None = None


class MessagingWhatsAppSetup(ResponseModel):
    mode: Literal["", "bot", "self-chat"]
    allowed_users_set: bool
    home_channel_set: bool


class MessagingPlatform(ResponseModel):
    """``_messaging_platform_payload`` for one ``_messaging_platform_catalog`` entry."""

    id: str
    name: str
    description: str
    docs_url: str
    enabled: bool
    configured: bool
    gateway_running: bool
    # ``disabled``/``not_configured``/``pending_restart``/``gateway_stopped``/``startup_failed``
    # or the live gateway's own per-platform state.
    state: str
    error_code: str | None
    error_message: str | None
    updated_at: str | None
    home_channel: MessagingHomeChannel | None
    env_vars: list[MessagingPlatformEnvVar]
    ingress_url: str | None
    whatsapp_setup: MessagingWhatsAppSetup | None = None


class MessagingPlatformsResponse(ResponseModel):
    """``get_messaging_platforms``."""

    env_path: str
    gateway_start_command: str
    platforms: list[MessagingPlatform]


class MessagingPlatformUpdateResponse(ResponseModel):
    """``update_messaging_platform``."""

    ok: bool
    platform: str
    hot_served: bool


class MessagingPlatformTestResponse(ResponseModel):
    """``test_messaging_platform`` — a verdict over the same payload as the platform list. A
    connected platform with a per-user authorization surface also carries ``auth_posture``
    (``_messaging_platform_posture``); ``ok`` stays true and ``message`` says what to configure."""

    ok: bool
    state: str
    message: str
    auth_posture: Literal["open", "allowlist", "pairing", "deny_all"] | None = None
