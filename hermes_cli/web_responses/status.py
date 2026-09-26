"""Response contracts for ``hermes_cli/web_routers/status.py`` (``router`` and ``logs_router``)."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from hermes_cli.web_responses.base import OkResponse, OpenModel, ResponseModel


class SshOwnershipResponse(ResponseModel):
    """``get_ssh_ownership``."""

    ok: bool
    sshOwnerNonce: str
    protocolVersion: int
    runtimeIntact: bool


class HealthResponse(ResponseModel):
    """``get_health``. ``commit`` is the code the process booted from (``VersionInfo.commit``;
    ``null`` when the install cannot name one)."""

    ok: bool
    version: str
    displayVersion: str
    commit: str | None
    auth_required: bool


class HostIdentityResponse(ResponseModel):
    """``get_host_identity``."""

    ok: bool
    protocolVersion: int
    pid: int
    role: str = Field(description='The published host role; "serve" when none was recorded.')
    servesSpa: bool


class HealthIdleResponse(ResponseModel):
    """``get_health_idle`` — ``{"ok": true}`` plus ``hermes_cli/web_server_idle_proof.py::idle_proof``.
    ``idle: null`` means a ledger was unreadable (treat as busy)."""

    ok: bool
    idle: bool | None
    reason: Literal[
        "turn_probe_unavailable", "turn_in_flight", "input_probe_unavailable", "awaiting_human_input"
    ] | None
    detail: str | None = None


class HealthRetirementResponse(ResponseModel):
    """``post_health_retirement`` — ``hermes_cli/backend_retirement.py::RetirementFence``
    ``prepare`` / ``commit`` / ``cancel``. Only ``prepare`` carries ``idle`` (``null`` = cannot
    prove idle) and, when it succeeded, ``token``."""

    ok: bool
    idle: bool | None = None
    token: str | None = None


class StatusApiServerMetricsToday(ResponseModel):
    """UTC-day counters; ``latency_p95_ms`` is null before the first request of the day."""

    day: str
    requests: int
    messages: int
    tokens: int
    latency_p95_ms: float | None


class StatusApiServerMetrics(ResponseModel):
    """``gateway/platforms/api_server.py::_api_server_status_payload`` — the only platform that
    publishes ``metrics`` today (``last_*`` are ISO timestamps)."""

    host: str
    port: int
    active_runs: int
    stored_runs: int
    last_request_at: str | None
    last_heartbeat: str | None
    metrics_today: StatusApiServerMetricsToday


class StatusGatewayPlatform(OpenModel):
    """One runtime platform entry (``gateway/status.py::_prepare_runtime_status_update``) with the
    writer-identity stamps stripped; mirrored api_server/webhook entries of a served profile add
    ``ingress_url`` / ``mirrored_from`` (``shared_listener_mirror_platforms``)."""

    state: str | None = None
    error_code: str | None = None
    error_message: str | None = None
    needs_attention: bool | None = None
    retrying_since: str | None = None
    metrics: StatusApiServerMetrics | None = None
    updated_at: str | None = None
    ingress_url: str | None = None
    listener_base: str | None = None
    mirrored_from: str | None = None


class StatusGatewayComponent(ResponseModel):
    status: Literal["ok", "degraded"]
    state: str


class StatusDashboardComponent(ResponseModel):
    """``hermes_cli/web_server.py::DashboardHealth.snapshot``."""

    status: Literal["ok", "degraded"]
    recent_unhandled_errors: int
    last_error_at: float | None
    selftest: Literal["unknown", "ok", "failing"]


class StatusStorageComponent(ResponseModel):
    """``gateway/readiness.py::_probe_state_db`` reduced to its status enum."""

    status: Literal["ok", "degraded"]
    reason: Literal["corrupt"] | None = None


class StatusPlatformsComponent(ResponseModel):
    status: Literal["ok", "degraded"]
    configured: int
    connected: int


class StatusComponents(ResponseModel):
    """``_component_health``."""

    gateway: StatusGatewayComponent
    dashboard: StatusDashboardComponent
    storage: StatusStorageComponent
    platforms: StatusPlatformsComponent


class StatusMemoryPressure(ResponseModel):
    """``gateway/memory_status.py::collect_memory_status``; only ``pressure`` when the collector
    raised."""

    pressure: Literal["ok", "elevated", "critical", "unknown"]
    gateway_rss_mb: int | None = None
    system_total_mb: int | None = None
    system_available_mb: int | None = None
    swap_used_mb: int | None = None
    sampled_at: str | None = None
    last_boot_unclean: bool = False
    last_boot_suspected_oom: bool = False
    boot_id: str | None = None


class StatusDiskPressure(ResponseModel):
    """``gateway/disk_status.py::collect_disk_status``; only ``pressure`` when the collector
    raised."""

    pressure: Literal["ok", "elevated", "critical", "unknown"]
    total_mb: int | None = None
    free_mb: int | None = None
    used_percent: float | None = None


class StatusFtsRebuild(ResponseModel):
    """``hermes_state_search.py::_rebuild_status``."""

    pending: bool
    total: int
    indexed: int
    percent: int


class StatusGatewayTopologyEntry(ResponseModel):
    """One live gateway from ``hermes_cli/web_server_gateway.py::_collect_profile_gateway_topology``."""

    profile: str
    ports: dict[str, int]
    served_profiles: list[str] | None = None


class StatusResponse(ResponseModel):
    """``get_status`` — the public liveness probe. The host-recon keys (``hermes_home`` …
    ``gateways``) are present only when the auth gate is off; ``install_id`` only when it could be
    persisted; ``fts_rebuild`` only while a deferred FTS rebuild is pending."""

    version: str
    release_date: str
    config_version: int
    latest_config_version: int
    can_update_hermes: bool
    gateway_running: bool
    gateway_state: str | None
    gateway_platforms: dict[str, StatusGatewayPlatform] = Field(
        description='Plain platform names plus validated "<profile>:<platform>" keys.')
    gateway_exit_reason: str | None
    gateway_updated_at: str | None
    gateway_heartbeat_stale_s: int | None
    gateway_shared_with: list[str] | None
    active_agents: int
    gateway_busy: bool
    gateway_drainable: bool
    restart_drain_timeout: float
    active_sessions: int
    auth_required: bool
    auth_providers: list[str]
    auth_flows: list[Literal["cookie", "native_pkce"]]
    nous_session_valid: Literal["valid", "terminal", "unknown"]
    install_id: str | None = None
    shared_profile_warning: bool
    components: StatusComponents
    overall: Literal["ok", "degraded"]
    memory: StatusMemoryPressure
    disk: StatusDiskPressure
    fts_rebuild: StatusFtsRebuild | None = None
    profiles: list[str]
    parked_profiles: list[str]
    gateway_mode: Literal["multiplex", "single", "multiple", "none", "unknown"]
    multiplex_standalone_reason: str | None
    hermes_home: str | None = None
    config_path: str | None = None
    env_path: str | None = None
    gateway_pid: int | None = None
    gateway_health_url: str | None = None
    gateways: list[StatusGatewayTopologyEntry] | None = None


class SystemStatsMemory(ResponseModel):
    total: int
    available: int
    used: int
    percent: float


class SystemStatsDisk(ResponseModel):
    total: int
    used: int
    free: int
    percent: float


class SystemStatsProcess(ResponseModel):
    pid: int
    rss: int
    create_time: int
    num_threads: int


class SystemStatsResponse(ResponseModel):
    """``get_system_stats``; every psutil-derived key is absent when psutil (or that probe) is
    unavailable."""

    os: str
    os_release: str
    os_version: str
    platform: str
    arch: str
    hostname: str
    python_version: str
    python_impl: str
    hermes_version: str
    cpu_count: int | None
    psutil: bool
    memory: SystemStatsMemory | None = None
    disk: SystemStatsDisk | None = None
    cpu_percent: float | None = None
    load_avg: list[float] | None = None
    uptime_seconds: int | None = None
    process: SystemStatsProcess | None = None


class CuratorStatusResponse(ResponseModel):
    """``get_curator_status``; a getter that raised reads as ``null``."""

    enabled: bool
    paused: bool
    interval_hours: int | None
    last_run_at: str | None
    min_idle_hours: float | None
    stale_after_days: int | None
    archive_after_days: int | None


class CuratorPausedResponse(OkResponse):
    """``set_curator_paused``."""

    paused: bool


class LearningGraphNode(ResponseModel):
    """A learned skill or a memory card; ``memorySource`` only on memory nodes."""

    id: str
    label: str
    kind: Literal["skill", "memory"]
    memorySource: Literal["memory", "profile"] | None = None
    timestamp: int | None
    category: str
    useCount: int
    state: str
    createdBy: str | None
    pinned: bool


class LearningGraphEdge(ResponseModel):
    source: str
    target: str


class LearningGraphCluster(ResponseModel):
    category: str
    count: int


class LearningGraphMemoryCard(ResponseModel):
    """``agent/learning_graph.py::_memory_cards``."""

    source: Literal["memory", "profile"]
    timestamp: int | None
    title: str
    body: str
    fingerprint: str


class LearningGraphStats(ResponseModel):
    """``agent/learning_graph.py::density_stats`` plus the memory counts."""

    nodes: int
    related_edges: int
    edges_per_node: float
    linked_nodes: int
    isolated_pct: float
    categories: int
    agent_created: int
    used: int
    top_categories: list[tuple[str, int]] = Field(description="Up to 8 ``[category, count]`` pairs.")
    memory_nodes: int
    memory_skill_edges: int
    learned_skills: int


class LearningGraphResponse(ResponseModel):
    """``agent/learning_graph.py::build_learning_graph``."""

    nodes: list[LearningGraphNode]
    edges: list[LearningGraphEdge]
    clusters: list[LearningGraphCluster]
    memory: list[LearningGraphMemoryCard]
    stats: LearningGraphStats


class LearningNodeDetailResponse(ResponseModel):
    """``agent/learning_mutations.py::node_detail`` (the non-ok results become a 404)."""

    ok: bool
    kind: Literal["skill", "memory"]
    id: str
    label: str
    content: str


class LearningNodeMutationResponse(ResponseModel):
    """``agent/learning_mutations.py::delete_node`` / ``edit_node`` (the non-ok results become
    a 400)."""

    ok: bool
    message: str


class PortalFeature(ResponseModel):
    label: str
    state: str = Field(description='"via Nous Portal", the active provider name, "active" or "not configured".')


class PortalStatusResponse(ResponseModel):
    """``_get_portal_status_sync``."""

    logged_in: bool
    portal_url: str | None
    inference_url: str | None
    provider: str
    free_tier: bool
    account_tier: str | None
    subscription_url: str
    features: list[PortalFeature]


class DebugShareResponse(OkResponse):
    """``run_debug_share_endpoint`` — ``hermes_cli/debug.py::DebugShareResult`` minus ``report``."""

    urls: dict[str, str] = Field(description='Label ("Report", "agent.log", …) → paste URL.')
    failures: list[str]
    redacted: bool
    auto_delete_seconds: int


class LogsResponse(ResponseModel):
    """``get_logs`` — raw log lines (trailing newline kept); ``[]`` when the file does not exist."""

    file: str
    lines: list[str]
