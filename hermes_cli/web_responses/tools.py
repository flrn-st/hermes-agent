"""Response contracts for ``hermes_cli/web_routers/tools.py``."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from hermes_cli.web_responses.base import JsonValue, ResponseModel


class ToolsetListRow(ResponseModel):
    """One ``get_toolsets`` row per ``hermes_cli/tools_config.py::_get_effective_configurable_toolsets``
    entry (built-ins, then plugin toolsets). ``available`` mirrors ``enabled``."""

    name: str
    label: str
    description: str
    platform: str = Field(description="Platform the toggle writes to (``cli`` unless platform-restricted).")
    platform_label: str
    enabled: bool
    available: bool
    configured: bool
    tools: list[str]


class ToolsetToggleResponse(ResponseModel):
    """``toggle_toolset``."""

    ok: bool
    name: str
    platform: str
    enabled: bool
    post_setup_started: str | None = Field(
        description="Post-setup key whose background install this enable started, else ``null``."
    )


ToolsetProviderReadiness = Literal["ready", "needs_keys", "needs_auth", "needs_setup"]


class ToolsetConfigEnvVar(ResponseModel):
    """A provider row's ``env_vars`` entry annotated with ``is_set`` (never the value)."""

    key: str
    prompt: str
    url: str | None
    default: str | None
    is_set: bool


class ToolsetConfigProvider(ResponseModel):
    """One provider picker row (``hermes_cli/tools_config_providers.py::_visible_providers``:
    ``TOOL_CATEGORIES`` rows, then plugin rows)."""

    name: str
    badge: str
    tag: str
    env_vars: list[ToolsetConfigEnvVar]
    post_setup: str | None
    requires_nous_auth: bool
    managed_nous_feature: str | None = Field(
        description="The Nous Subscription feature a managed row rides (\"web\", \"tts\", ...); null on BYOK rows.")
    is_active: bool
    status: ToolsetProviderReadiness = Field(
        description="``hermes_cli/tools_config_providers.py::provider_readiness_status``."
    )
    web_backend: str | None = Field(default=None, description="``web`` rows with a backend key only.")
    capabilities: list[Literal["search", "extract"]] | None = Field(
        default=None, description="``web`` rows only: ``web_provider_capabilities(web_backend)``."
    )
    tts_provider: str | None = Field(default=None, description="``tts`` rows only: the ``tts.provider`` value.")


class ToolsetConfigResponse(ResponseModel):
    """``get_toolset_config`` — ``has_category: false`` (empty ``providers``) for toolsets without a
    provider category; the active backends are resolved only for ``web``."""

    name: str
    has_category: bool
    providers: list[ToolsetConfigProvider]
    active_provider: str | None
    active_search_backend: str | None = None
    active_extract_backend: str | None = None
    search_via_nous: bool | None = Field(None, description="``web`` only: the search backend rides the Nous Tool Gateway.")
    extract_via_nous: bool | None = Field(None, description="``web`` only: the extract backend rides the Nous Tool Gateway.")


class ToolsetModelOption(ResponseModel):
    """One catalog model (``display`` defaults to the id; the other labels to ``""``)."""

    id: str
    display: str
    speed: str
    strengths: str
    price: str


class ToolsetModelsResponse(ResponseModel):
    """``get_toolset_models`` — ``_no_models`` (``has_models: false``, no ``provider``/``plugin``)
    when the toolset has no catalog or no model-capable backend resolves."""

    name: str
    has_models: bool
    models: list[ToolsetModelOption]
    current: str | None
    default: str | None
    provider: str | None = None
    plugin: str | None = None


class ToolsetModelSelectResponse(ResponseModel):
    """``select_toolset_model``."""

    ok: bool
    name: str
    model: str
    plugin: str


class ToolsetProviderSelectResponse(ResponseModel):
    """``select_toolset_provider`` — ``needs_nous_auth`` + ``feature`` only for a managed Nous row the
    account is not entitled to."""

    ok: bool
    name: str
    provider: str
    capability: Literal["search", "extract"] | None = None
    needs_nous_auth: bool | None = None
    feature: str | None = None


class ToolsetEnvSaveResponse(ResponseModel):
    """``save_toolset_env``."""

    ok: bool
    name: str
    saved: list[str]
    skipped: list[str] = Field(description="Keys submitted blank (left unchanged).")
    is_set: dict[str, bool] = Field(description="Every env var the toolset's providers declare -> set?")


class ToolsetPostSetupResponse(ResponseModel):
    """``run_toolset_post_setup`` — ``hermes_cli/web_routers/_common.py::spawn_profile_action`` plus
    the post-setup ``key``; tail via ``GET /api/actions/tools-post-setup/status``."""

    ok: bool
    pid: int
    name: str
    key: str


class TerminalBackendRow(ResponseModel):
    """A built-in (``hermes_cli/web_server_profiles.py::_TERMINAL_BACKENDS``) or plugin backend with
    its health probe."""

    name: str
    label: str
    description: str
    active: bool
    status: str = Field(
        description='"ready", "needs_setup" or "unavailable" (plugin backends supply their own probe).'
    )
    detail: str


class TerminalBackendsResponse(ResponseModel):
    """``get_terminal_backends``."""

    active: str
    backends: list[TerminalBackendRow]


class TerminalBackendSelectResponse(ResponseModel):
    """``select_terminal_backend``."""

    ok: bool
    backend: str


class ComputerUseCheck(ResponseModel):
    """One ``cua-driver doctor --json`` probe, stringified by
    ``tools/computer_use/permissions.py::_doctor``."""

    label: str
    status: str
    message: str


class ComputerUseStatusResponse(ResponseModel):
    """``tools/computer_use/permissions.py::computer_use_status``; the TCC booleans are macOS-only
    (``null`` elsewhere or when unknown)."""

    platform: str
    platform_supported: bool
    installed: bool
    version: str | None
    ready: bool | None = Field(description="``null`` = unknown (driver missing or probe failed).")
    can_grant: bool
    checks: list[ComputerUseCheck]
    source: dict[str, JsonValue] | None = Field(description="cua-driver's own ``source`` block, verbatim.")
    error: str | None
    accessibility: bool | None
    screen_recording: bool | None
    screen_recording_capturable: bool | None
