"""Response contracts for ``hermes_cli/web_routers/ops.py`` (pairing, webhooks, gateway lifecycle,
credential pool, memory status and operations)."""

from __future__ import annotations

from hermes_cli.web_responses.base import ActionSpawnResponse, OkResponse, OpenModel, ResponseModel
from hermes_cli.web_responses.memory_providers import MemoryProviderStatusRow

# --- Pairing (``gateway/pairing.py::PairingStore``)


class UserPairingPendingRow(ResponseModel):
    """``PairingStore.list_pending``; ``request_id`` is ``""`` for legacy pre-hash entries (never the
    code itself)."""

    platform: str
    request_id: str
    user_id: str
    user_name: str
    age_minutes: int


class UserPairingApprovedRow(OpenModel):
    """``PairingStore.list_approved`` — the stored ``{user_name, approved_at}`` record spread over
    ``platform``/``user_id``; ``approved_at`` is epoch seconds."""

    platform: str
    user_id: str
    user_name: str
    approved_at: float


class UserPairingListResponse(ResponseModel):
    """``list_pairing``."""

    pending: list[UserPairingPendingRow]
    approved: list[UserPairingApprovedRow]


class UserPairingApprovedUser(ResponseModel):
    """``PairingStore._finish_approval``."""

    user_id: str
    user_name: str


class UserPairingApproveResponse(OkResponse):
    """``approve_pairing``."""

    user: UserPairingApprovedUser


class UserPairingClearResponse(OkResponse):
    """``clear_pending_pairing`` — ``cleared`` counts the removed pending requests."""

    cleared: int


# --- Webhooks (``hermes_cli/webhook.py`` subscription store)


class WebhookSubscription(ResponseModel):
    """``_webhook_route_summary``; ``created_at`` is ``None`` for a hand-written route without one."""

    name: str
    description: str
    events: list[str]
    deliver: str
    deliver_only: bool
    prompt: str
    script: str
    skills: list[str]
    created_at: str | None
    url: str
    secret_set: bool
    enabled: bool


class WebhookListResponse(ResponseModel):
    """``list_webhooks``."""

    enabled: bool
    base_url: str
    subscriptions: list[WebhookSubscription]


class WebhookCreateResponse(WebhookSubscription):
    """``create_webhook`` — the summary plus the HMAC secret, surfaced only here."""

    secret: str


class WebhookEnableResponse(OkResponse):
    """``enable_webhooks`` — spreads ``hermes_cli/web_server_gateway.py::_restart_gateway_after``:
    ``restart_action``/``restart_pid`` when the restart spawned, ``restart_error`` when it failed."""

    platform: str
    enabled: bool
    needs_restart: bool
    restart_started: bool
    restart_action: str | None = None
    restart_pid: int | None = None
    restart_error: str | None = None


class WebhookEnabledToggleResponse(OkResponse):
    """``set_webhook_enabled``."""

    name: str
    enabled: bool


# --- Spawned background actions (``hermes_cli/web_routers/_common.py::spawn_profile_action`` and
# the gateway lifecycle verbs); logs are tailed via ``/api/actions/{name}/status``.


class OpsBackupResponse(ActionSpawnResponse):
    """``run_backup``; ``archive`` only when the dashboard chose the output path (no ``output``
    in the request), so the UI can offer ``/api/ops/backup/download``."""

    archive: str | None = None


class OpsImportUploadResponse(ActionSpawnResponse):
    """``run_import_upload`` — the staged archive path and its size in bytes."""

    archive: str
    uploaded_bytes: int


# --- Credential pool (``agent/credential_pool.py::PooledCredential``, redacted)


class CredentialPoolEntrySummary(ResponseModel):
    """``_pool_entry_summary``; ``index`` is 1-based (``CredentialPool.remove_index``)."""

    index: int
    id: str
    label: str
    auth_type: str
    source: str
    priority: int
    last_status: str | None
    request_count: int
    token_preview: str
    has_refresh: bool


class CredentialPoolProvider(ResponseModel):
    provider: str
    entries: list[CredentialPoolEntrySummary]


class CredentialPoolListResponse(ResponseModel):
    """``list_credential_pool`` — providers with at least one pooled entry."""

    providers: list[CredentialPoolProvider]


class CredentialPoolAddResponse(OkResponse):
    """``add_credential_pool_entry`` — ``count`` is the provider's pool size after the add."""

    provider: str
    count: int


class CredentialPoolRemoveResponse(OkResponse):
    """``remove_credential_pool_entry`` — ``cleaned``/``hints`` come from the source's RemovalStep."""

    provider: str
    count: int
    cleaned: list[str]
    hints: list[str]


# --- Built-in memory


class MemoryBuiltinFileSizes(ResponseModel):
    """Byte size of ``memories/MEMORY.md`` / ``memories/USER.md`` (0 when absent)."""

    memory: int
    user: int


class MemoryStatusResponse(ResponseModel):
    """``get_memory_status``; ``active`` is ``""`` for the built-in provider."""

    active: str
    providers: list[MemoryProviderStatusRow]
    builtin_files: MemoryBuiltinFileSizes


class MemoryProviderSelectResponse(OkResponse):
    """``set_memory_provider``; ``active`` is ``""`` for the built-in provider."""

    active: str


class MemoryResetResponse(OkResponse):
    """``reset_memory`` — the file names actually deleted."""

    deleted: list[str]


# --- Shell hooks (``agent/shell_hooks.py``)


class OpsShellHook(ResponseModel):
    """One ``list_hooks`` row (``ShellHookSpec`` + consent state); ``approved_at`` is the ISO
    timestamp from the allowlist entry."""

    event: str
    matcher: str | None
    command: str
    timeout: int
    allowed: bool
    approved_at: str | None
    executable: bool


class OpsShellHookListResponse(ResponseModel):
    """``list_hooks``; ``valid_events`` is ``[]`` when the plugin hook registry cannot be imported."""

    hooks: list[OpsShellHook]
    valid_events: list[str]


class OpsShellHookCreateResponse(OkResponse):
    """``create_hook``; ``approved`` is False when consent was not requested or recording it failed."""

    event: str
    command: str
    approved: bool


# --- Checkpoints


class OpsCheckpointSession(ResponseModel):
    session: str
    files: int
    bytes: int


class OpsCheckpointListResponse(ResponseModel):
    """``list_checkpoints`` — per-session file count and size of the /rollback shadow store."""

    sessions: list[OpsCheckpointSession]
    total_bytes: int
