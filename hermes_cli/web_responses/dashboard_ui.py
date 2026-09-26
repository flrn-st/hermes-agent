"""Response contracts for ``hermes_cli/web_routers/dashboard_ui.py``."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from hermes_cli.web_responses.base import OkResponse, ResponseModel
from hermes_cli.web_responses.memory_providers import MemoryProviderStatusRow

# ── themes / font ─────────────────────────────────────────────────────────────────────────────


class DashboardThemeLayer(ResponseModel):
    """``hermes_cli/web_server_dashboard.py::_parse_theme_layer`` — alpha clamped to 0..1."""

    hex: str
    alpha: float


class DashboardThemePalette(ResponseModel):
    background: DashboardThemeLayer
    midground: DashboardThemeLayer
    foreground: DashboardThemeLayer
    warmGlow: str
    noiseOpacity: float


class DashboardThemeTypography(ResponseModel):
    """Defaults (``_THEME_DEFAULT_TYPOGRAPHY``) overlaid with the non-empty YAML strings."""

    fontSans: str
    fontMono: str
    baseSize: str
    lineHeight: str
    letterSpacing: str
    fontDisplay: str | None = None
    fontUrl: str | None = None


class DashboardThemeLayout(ResponseModel):
    radius: str
    density: Literal["compact", "comfortable", "spacious"]


class DashboardThemeAssets(ResponseModel):
    """Only non-empty named slots are sent; ``custom`` keys are CSS identifiers."""

    bg: str | None = None
    hero: str | None = None
    logo: str | None = None
    crest: str | None = None
    sidebar: str | None = None
    header: str | None = None
    custom: dict[str, str] | None = None


class DashboardThemeDefinition(ResponseModel):
    """``hermes_cli/web_server_dashboard.py::_normalise_theme_definition`` — the wire format
    ``ThemeProvider`` consumes. ``label`` falls back to ``name``; ``description`` is the raw YAML
    value (``null`` when the key is present but empty)."""

    name: str
    label: str
    description: str | None
    palette: DashboardThemePalette
    typography: DashboardThemeTypography
    layout: DashboardThemeLayout
    layoutVariant: Literal["standard", "cockpit", "tiled"]
    colorOverrides: dict[str, str] | None = None
    assets: DashboardThemeAssets | None = None
    customCSS: str | None = None
    componentStyles: dict[str, dict[str, str]] | None = None


class DashboardThemeEntry(ResponseModel):
    """A built-in (``_BUILTIN_DASHBOARD_THEMES``: no ``definition``, the frontend owns it) or a
    user theme from ``dashboard-themes/*.yaml`` (with its normalised ``definition``)."""

    name: str
    label: str
    description: str | None
    definition: DashboardThemeDefinition | None = None


class DashboardThemesResponse(ResponseModel):
    """``get_dashboard_themes``; ``active`` is ``dashboard.theme`` as stored in config.yaml."""

    themes: list[DashboardThemeEntry]
    active: str


class DashboardThemeSetResponse(OkResponse):
    """``set_dashboard_theme``."""

    theme: str


class DashboardFontResponse(ResponseModel):
    """``get_dashboard_font`` — a ``_FONT_CHOICES`` id, or ``"theme"``."""

    font: str


class DashboardFontSetResponse(OkResponse):
    """``set_dashboard_font`` — the stored id (unknown ids coerce to ``"theme"``)."""

    font: str


# ── dashboard plugin manifests ────────────────────────────────────────────────────────────────


class DashboardPluginTab(ResponseModel):
    """``_dashboard_plugin_entry`` tab info; ``override`` only when it is an absolute route,
    ``hidden`` only when true."""

    path: str
    position: str
    override: str | None = None
    hidden: bool | None = None


class DashboardPluginManifest(ResponseModel):
    """``hermes_cli/web_server_dashboard.py::_dashboard_plugin_entry`` with the internal ``_*``
    keys stripped. String fields are the manifest.json values (defaults when absent)."""

    name: str
    label: str
    description: str
    icon: str
    version: str
    tab: DashboardPluginTab
    slots: list[str]
    entry: str
    css: str | None
    has_api: bool
    source: Literal["user", "bundled", "project"]


class DashboardPluginsRescanResponse(OkResponse):
    """``rescan_dashboard_plugins``."""

    count: int


# ── plugins hub ───────────────────────────────────────────────────────────────────────────────

PluginRuntimeStatus = Literal["enabled", "disabled", "inactive"]


class PluginsHubPluginRow(ResponseModel):
    """One ``hermes_cli/web_server_dashboard.py::_merged_plugins_hub`` agent-plugin row."""

    name: str
    version: str
    description: str
    source: Literal["bundled", "user", "git", "entrypoint"]
    runtime_status: PluginRuntimeStatus
    has_dashboard_manifest: bool
    dashboard_manifest: DashboardPluginManifest | None
    path: str
    can_remove: bool
    can_update_git: bool
    auth_required: bool
    auth_command: str
    user_hidden: bool
    removed_reason: str | None


class PluginsHubContextOption(ResponseModel):
    """``hermes_cli/plugins_cmd_toggle.py::_discover_context_engines`` pair."""

    name: str
    description: str


class PluginsHubProviders(ResponseModel):
    """``memory_provider`` is ``""`` for the built-in provider; ``context_engine`` defaults to
    ``"compressor"``."""

    memory_provider: str
    memory_options: list[MemoryProviderStatusRow]
    context_engine: str
    context_options: list[PluginsHubContextOption]


class PluginsHubResponse(ResponseModel):
    """``hermes_cli/web_server_dashboard.py::_merged_plugins_hub``."""

    plugins: list[PluginsHubPluginRow]
    orphan_dashboard_plugins: list[DashboardPluginManifest]
    providers: PluginsHubProviders


# ── plugin catalog ────────────────────────────────────────────────────────────────────────────


class PluginCatalogCapabilities(ResponseModel):
    """``hermes_cli/plugin_catalog.py::CatalogCapabilities``."""

    provides_tools: list[str]
    provides_hooks: list[str]
    provides_middleware: list[str]
    requires_env: list[str]


class PluginCatalogEntryRow(ResponseModel):
    """``PluginCatalogEntry.to_dict()`` merged with local state by
    ``hermes_cli/plugins_cmd_catalog.py::installed_catalog_state``. ``tier``/``category`` are
    enforced by ``plugin_catalog.entry_from_mapping``."""

    name: str
    repo: str
    sha: str
    description: str
    maintainer: str
    tier: Literal["official", "community"]
    category: Literal["desktop", "memory", "platform", "web", "tools", "voice", "automation", "models", "general"]
    requires_hermes: str
    subdir: str
    docs_url: str
    version: str
    image: str
    screenshots: list[str]
    readme: bool
    platforms: list[str]
    title: str
    onboarding: bool
    capabilities: PluginCatalogCapabilities
    known_issues: list[str]
    sha_short: str
    capability_summary: str
    installed: bool
    installed_sha: str | None
    update_available: bool
    runtime_status: PluginRuntimeStatus | None


class PluginCatalogRemovedRow(ResponseModel):
    """``hermes_cli/plugin_catalog.py::RemovedEntry`` (kill list)."""

    name: str
    repo: str
    reason: str
    date: str


class PluginCatalogResponse(ResponseModel):
    """``hermes_cli/plugins_cmd_catalog.py::installed_catalog_state``; ``generated_at`` is ISO-8601
    UTC with a ``Z`` suffix."""

    entries: list[PluginCatalogEntryRow]
    removed: list[PluginCatalogRemovedRow]
    generated_at: str


# ── agent-plugin mutations ────────────────────────────────────────────────────────────────────


class AgentPluginLiveServer(ResponseModel):
    """``hermes_cli/plugins_activation_live.py::connect_plugin_mcp`` row. Mirrors
    ``tui_gateway/contracts/tools_mcp_plugins.py::PluginLiveServer``."""

    name: str
    connected: bool
    tools: list[str]
    error: str | None = None


class AgentPluginLiveSkill(ResponseModel):
    """``hermes_cli/plugins_activation_live.py::plugin_skills`` row (``PluginLiveSkill``)."""

    name: str
    description: str


class AgentPluginLiveNow(ResponseModel):
    mcp_servers: list[AgentPluginLiveServer]
    skills: list[AgentPluginLiveSkill]


class AgentPluginActivation(ResponseModel):
    """``hermes_cli/plugins_activation.py::plugin_activation_summary`` (+ ``live_now`` when this
    process loaded it via ``load_and_go_live``; absent when taken from the gateway's answer).
    Mirrors ``tui_gateway/contracts/tools_mcp_plugins.py::PluginActivation``."""

    name: str
    key: str
    activated_now: dict[str, list[str]]
    deferred: dict[str, list[str]]
    live_now: AgentPluginLiveNow | None = None


class AgentPluginInstallResponse(ResponseModel):
    """``hermes_cli/plugins_cmd_install.py::dashboard_install_plugin`` ok payload (``ok: false``
    becomes a 400) with ``after_install_path`` stripped by the route. The activation trio comes
    from ``plugins_activation.activate_plugin_now`` (or its not-enabled stand-in)."""

    ok: bool
    plugin_name: str
    warnings: list[str]
    python_dependencies: list[str]
    missing_env: list[str]
    enabled: bool
    gateway_reloaded: bool
    activation: AgentPluginActivation | None
    restart_required: bool
    known_issues: list[str] = Field(description="The catalog entry's known issues; empty for a non-catalog install.")


class AgentPluginToggleResponse(ResponseModel):
    """``hermes_cli/plugins_cmd.py::dashboard_set_agent_plugin_enabled`` ok payload; ``name`` is
    the canonical key written. An enable that changed config also carries ``gateway_reloaded`` +
    ``activation``; ``ok: false`` becomes a 400."""

    ok: bool
    name: str
    unchanged: bool
    restart_required: bool
    gateway_reloaded: bool | None = None
    activation: AgentPluginActivation | None = None


class AgentPluginUpdateResponse(ResponseModel):
    """``hermes_cli/plugins_cmd_update.py::dashboard_update_user_plugin``: a catalog re-pin
    (``sha``, deps, warnings, plus the activation trio when it changed), a ``git pull``
    (``output``), or ``ok: false`` + ``consent_required`` with the ``delta`` a widened pin adds —
    the only ``ok: false`` answer that is not turned into a 400."""

    ok: bool
    name: str
    unchanged: bool | None = None
    sha: str | None = None
    python_dependencies: list[str] | None = None
    warnings: list[str] | None = None
    gateway_reloaded: bool | None = None
    activation: AgentPluginActivation | None = None
    restart_required: bool | None = None
    output: str | None = None
    consent_required: bool | None = None
    error: str | None = None
    delta: dict[str, list[str]] | None = None
    delta_lines: list[str] | None = None


class AgentPluginRemoveResponse(OkResponse):
    """``hermes_cli/plugins_cmd_remove.py::_remove_user_plugin``; ``cleared_memory_provider``
    only when the removed plugin was the selected ``memory.provider``."""

    name: str
    cleared_memory_provider: bool | None = None


class AgentPluginActivateResponse(OkResponse):
    """``post_agent_plugin_activate`` — ``activation`` is ``None`` when the plugin did not load."""

    activation: AgentPluginActivation | None


class PluginVisibilityResponse(OkResponse):
    """``post_plugin_visibility``."""

    name: str
    hidden: bool
