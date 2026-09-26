"""Response contracts for ``hermes_cli/web_routers/mcp.py``."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from hermes_cli.web_responses.base import JsonValue, ResponseModel


class McpServerConfigSummary(ResponseModel):
    """``hermes_cli/web_server_mcp.py::_mcp_server_summary`` — a configured server with stdio ``env``
    values redacted. Sibling of the ``mcp.servers.list`` JSON-RPC row
    (``tui_gateway/contracts/tools_mcp_plugins.py::McpServerSummary``), which lists env key names
    instead of redacted values."""

    name: str
    transport: Literal["http", "stdio", "unknown"]
    url: str | None
    command: str | None
    args: list[str]
    env: dict[str, str] = Field(description="Env var name -> redacted value (``redact_key``).")
    auth: str | None = Field(
        description='``mcp_servers.<name>.auth`` as written, or ``"header"`` when an Authorization '
        "header is configured."
    )
    enabled: bool
    tools: JsonValue | None = Field(
        description="``mcp_servers.<name>.tools`` as written (include/exclude filter); ``null`` = all tools."
    )
    source: Literal["config", "plugin"]
    plugin: str | None


class McpServerListResponse(ResponseModel):
    """``list_mcp_servers`` — sorted by name."""

    servers: list[McpServerConfigSummary]


class McpServerAddResponse(McpServerConfigSummary):
    """``add_mcp_server`` — the summary of the server just saved (always ``source: "config"``)."""


class McpToolSummary(ResponseModel):
    """A ``(name, description)`` pair from ``hermes_cli/mcp_config.py::_probe_single_server``
    (description truncated to 80 chars, ``""`` when absent)."""

    name: str
    description: str


class McpServerProbeTool(McpToolSummary):
    schema_chars: int | None = Field(
        default=None, description="Size of the registered tool schema; omitted when it could not be measured."
    )


class McpServerTestResponse(ResponseModel):
    """``test_mcp_server`` — ``ok: false`` carries ``error`` and an empty ``tools``; the prompt and
    resource counts are only reported on success."""

    ok: bool
    tools: list[McpServerProbeTool]
    error: str | None = None
    prompts: int | None = None
    resources: int | None = None


McpOAuthFlowState = Literal["starting", "authorization_required", "approved", "error"]


class McpOAuthFlowResponse(ResponseModel):
    """``auth_mcp_server`` — ``tools/mcp_dashboard_oauth.py::DashboardOAuthFlow.snapshot``."""

    flow_id: str
    server_name: str
    status: McpOAuthFlowState
    authorization_url: str | None
    error: str | None


class McpOAuthFlowStatusResponse(McpOAuthFlowResponse):
    """``mcp_oauth_flow_status`` — the flow snapshot plus the tools probed once approved
    (``[]`` until then)."""

    tools: list[McpToolSummary]


class McpOAuthCancelResponse(ResponseModel):
    """``cancel_mcp_oauth_flow`` — ``expired`` for an unknown/GC'd flow; otherwise the flow's status
    after cancelling (``approved`` if it had already completed)."""

    ok: bool
    status: Literal["expired", "approved", "error"]


class McpServerEnabledResponse(ResponseModel):
    """``set_mcp_server_enabled``."""

    ok: bool
    name: str
    enabled: bool


class McpCatalogRequiredEnv(ResponseModel):
    """``hermes_cli/mcp_catalog.py::EnvVarSpec`` (names and prompts only, never values)."""

    name: str
    prompt: str
    required: bool


class McpCatalogSuggest(ResponseModel):
    """``hermes_cli/mcp_catalog.py::SuggestSpec``."""

    keywords: list[str]
    hosts: list[str]
    applications: list[str]
    examples: list[str]
    requires_app: bool


class McpCatalogEntryRow(ResponseModel):
    """``hermes_cli/web_routers/mcp.py::_catalog_entry_json`` over a parsed
    ``hermes_cli/mcp_catalog.py::CatalogEntry``."""

    name: str
    description: str
    connector_slug: str | None
    source: str
    transport: Literal["stdio", "http"]
    auth_type: Literal["api_key", "oauth", "none"]
    required_env: list[McpCatalogRequiredEnv]
    command: str | None
    args: list[str]
    url: str | None
    install_url: str | None
    install_ref: str | None
    bootstrap: list[str]
    default_enabled: list[str] | None
    post_install: str
    suggest: McpCatalogSuggest | None
    needs_install: bool
    installed: bool
    enabled: bool


class McpCatalogDiagnostic(ResponseModel):
    """``hermes_cli/mcp_catalog.py::catalog_diagnostics`` — a manifest skipped by ``list_catalog``."""

    name: str
    kind: Literal["future_manifest", "invalid"]
    message: str


class McpCatalogResponse(ResponseModel):
    """``list_mcp_catalog``."""

    entries: list[McpCatalogEntryRow]
    diagnostics: list[McpCatalogDiagnostic]


class McpCatalogInstallResponse(ResponseModel):
    """``install_mcp_catalog_entry`` — git-bootstrap entries install in a background action
    (``background: true`` + ``action``); others install synchronously."""

    ok: bool
    name: str
    background: bool
    action: str | None = Field(
        default=None, description="Background action name, tailed via ``GET /api/actions/{action}/status``."
    )
