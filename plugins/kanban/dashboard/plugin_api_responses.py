"""Response contracts for ``plugin_api.py`` (mounted at ``/api/plugins/kanban``). Documentation
only, attached with ``responses=``; the modelling rules are ``hermes_cli/web_responses/base.py``'s.

Task / run / comment / event / attachment rows are ``hermes_cli/kanban_db.py`` dataclasses sent
through ``asdict``; they are modelled once here and reused by every route that returns them.
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from hermes_cli.web_responses.base import JsonValue, OpenModel, ResponseModel

KanbanDiagnosticSeverity = Literal["warning", "error", "critical"]  # kanban_diagnostics.SEVERITY_ORDER


# --- Rows shared across routes ------------------------------------------------


class KanbanTaskAge(ResponseModel):
    """``kanban_db.task_age`` — seconds; negative when a timestamp is in the future."""

    created_age_seconds: int | None
    started_age_seconds: int | None
    time_to_complete_seconds: int | None


class KanbanTask(ResponseModel):
    """``plugin_api._task_dict``: ``asdict(kanban_db.Task)`` plus the derived ``age`` and the
    newest run ``latest_summary`` (a 200-char preview on ``/board``, the full text elsewhere)."""

    id: str
    title: str
    body: str | None
    assignee: str | None
    status: str
    priority: int
    created_by: str | None
    created_at: int | None  # null only for an unparseable stamp
    started_at: int | None
    completed_at: int | None
    workspace_kind: str
    workspace_path: str | None
    claim_lock: str | None
    claim_expires: int | None
    tenant: str | None
    branch_name: str | None
    project_id: str | None
    result: str | None
    idempotency_key: str | None
    consecutive_failures: int
    worker_pid: int | None
    last_failure_error: str | None
    max_runtime_seconds: int | None
    last_heartbeat_at: int | None
    current_run_id: int | None
    workflow_template_id: str | None
    current_step_key: str | None
    skills: list[str] | None
    model_override: str | None
    provider_override: str | None
    reasoning_effort: str | None
    max_retries: int | None
    goal_mode: bool
    goal_max_turns: int | None
    session_id: str | None
    block_kind: str | None
    block_recurrences: int
    completion_contract: str | None
    age: KanbanTaskAge
    latest_summary: str | None
    current_run_started_at: int | None = Field(
        description="Start of the run ``current_run_id`` points at (``started_at`` is the first-ever start).")


class KanbanDiagnosticAction(ResponseModel):
    """``kanban_diagnostics.DiagnosticAction.to_dict``; ``payload`` is per-``kind``."""

    kind: str
    label: str
    payload: dict[str, JsonValue]
    suggested: bool


class KanbanDiagnostic(ResponseModel):
    """``kanban_diagnostics.Diagnostic.to_dict`` — one active distress signal on a task."""

    kind: str
    severity: KanbanDiagnosticSeverity
    title: str
    detail: str
    actions: list[KanbanDiagnosticAction]
    first_seen_at: int
    last_seen_at: int
    count: int
    run_id: int | None
    data: dict[str, JsonValue]


class KanbanWarningsSummary(ResponseModel):
    """``plugin_api._warnings_summary_from_diagnostics`` — the card badge."""

    count: int
    kinds: dict[str, int]
    latest_at: int
    highest_severity: KanbanDiagnosticSeverity | None


class KanbanTaskWithDiagnostics(KanbanTask):
    """``_task_dict`` after ``_attach_diagnostics``: both keys only when the task has diagnostics."""

    diagnostics: list[KanbanDiagnostic] | None = None
    warnings: KanbanWarningsSummary | None = None


class KanbanLinkCounts(ResponseModel):
    parents: int
    children: int


class KanbanChildProgress(ResponseModel):
    done: int
    total: int


class KanbanBoardCard(KanbanTaskWithDiagnostics):
    """A ``/board`` card: the task plus the per-board rollups ``get_board`` joins in."""

    link_counts: KanbanLinkCounts
    comment_count: int
    progress: KanbanChildProgress | None


class KanbanRun(ResponseModel):
    """``asdict(kanban_db.Run)`` — one attempt at a task (``task_runs`` row)."""

    id: int
    task_id: str
    profile: str | None
    step_key: str | None
    status: str
    claim_lock: str | None
    claim_expires: int | None
    worker_pid: int | None
    max_runtime_seconds: int | None
    last_heartbeat_at: int | None
    started_at: int
    ended_at: int | None
    outcome: str | None
    summary: str | None
    metadata: dict[str, JsonValue] | None
    error: str | None


class KanbanComment(ResponseModel):
    """``asdict(kanban_db.Comment)``."""

    id: int
    task_id: str
    author: str
    body: str
    created_at: int


class KanbanEvent(ResponseModel):
    """``asdict(kanban_db.Event)``; ``payload`` is per-``kind``."""

    id: int
    task_id: str
    kind: str
    payload: dict[str, JsonValue] | None
    created_at: int
    run_id: int | None


class KanbanAttachment(ResponseModel):
    """``plugin_api._attachment_dict``; ``stored_path`` is the absolute path workers read."""

    id: int
    task_id: str
    filename: str
    content_type: str | None
    size: int
    uploaded_by: str | None
    stored_path: str
    created_at: int


class KanbanBoardMeta(OpenModel):
    """``kanban_db.read_board_metadata``: the user-editable ``board.json`` merged over these
    defaults, so extra keys pass through."""

    slug: str
    name: str
    description: str
    icon: str
    color: str
    default_workdir: str | None
    project_id: str | None
    created_at: int | None
    archived: bool
    db_path: str


class KanbanBoard(KanbanBoardMeta):
    """``plugin_api._annotate_board_meta`` (create / rename)."""

    default_workspace_kind: Literal["scratch", "worktree", "dir"]
    project_name: str | None


class KanbanBoardListRow(KanbanBoard):
    """One ``list_boards`` row; ``counts`` is ``{status: n}`` incl. archived, ``total`` excludes it."""

    is_current: bool
    counts: dict[str, int]
    total: int


class KanbanHomeChannel(ResponseModel):
    """``plugin_api._configured_home_channels`` row; ``thread_id`` is ``""`` when unset."""

    platform: str
    chat_id: str
    thread_id: str
    name: str


# --- Board / tasks --------------------------------------------------------------


class KanbanBoardColumn(ResponseModel):
    name: Literal["triage", "todo", "scheduled", "ready", "running", "blocked", "review", "done", "archived"]
    tasks: list[KanbanBoardCard]


class KanbanBoardResponse(ResponseModel):
    """``plugin_api.get_board`` — ``archived`` column only with ``include_archived``."""

    columns: list[KanbanBoardColumn]
    tenants: list[str]
    assignees: list[str]
    latest_event_id: int
    now: int


class KanbanTaskLinks(ResponseModel):
    """``plugin_api._links_for``."""

    parents: list[str]
    children: list[str]


class KanbanLinkedTask(ResponseModel):
    """``plugin_api._link_tasks`` row."""

    id: str
    title: str
    status: str


class KanbanChildResult(ResponseModel):
    id: str
    title: str
    status: str
    latest_summary: str | None
    result: str | None


class KanbanTaskDetailResponse(ResponseModel):
    """``plugin_api.get_task`` — the drawer payload."""

    task: KanbanTaskWithDiagnostics
    comments: list[KanbanComment]
    events: list[KanbanEvent]
    attachments: list[KanbanAttachment]
    links: KanbanTaskLinks
    link_tasks: list[KanbanLinkedTask]
    child_results: list[KanbanChildResult]
    runs: list[KanbanRun]


class KanbanTaskCreateResponse(ResponseModel):
    """``plugin_api.create_task``; ``warning`` when a ready+assigned task has no dispatcher."""

    task: KanbanTask | None
    warning: str | None = None


class KanbanTaskUpdateResponse(ResponseModel):
    """``plugin_api.update_task``."""

    task: KanbanTask | None


class KanbanTaskDeleteResponse(ResponseModel):
    """``plugin_api.delete_task``."""

    deleted: bool
    task_id: str


class KanbanAttachmentListResponse(ResponseModel):
    """``plugin_api.list_task_attachments``."""

    attachments: list[KanbanAttachment]


class KanbanAttachmentUploadResponse(ResponseModel):
    """``plugin_api.upload_task_attachment``."""

    attachment: KanbanAttachment | None


class KanbanAttachmentDeleteResponse(ResponseModel):
    """``plugin_api.remove_attachment``."""

    ok: bool
    id: int


class KanbanLinkAddResponse(ResponseModel):
    """``plugin_api.add_link``; ``gated`` = the link demoted a ready child back to ``todo``."""

    ok: bool
    gated: bool


class KanbanBulkResult(ResponseModel):
    id: str
    ok: bool
    error: str | None = None


class KanbanBulkUpdateResponse(ResponseModel):
    """``plugin_api.bulk_update`` — one outcome per id."""

    results: list[KanbanBulkResult]


class KanbanTaskDiagnostics(ResponseModel):
    """``list_diagnostics`` row; the task columns are ``None`` if the task vanished mid-read."""

    task_id: str
    task_title: str | None
    task_status: str | None
    task_assignee: str | None
    diagnostics: list[KanbanDiagnostic]


class KanbanDiagnosticsResponse(ResponseModel):
    """``plugin_api.list_diagnostics``; ``count`` is the number of diagnostics, not tasks."""

    diagnostics: list[KanbanTaskDiagnostics]
    count: int


# --- Workers / runs / recovery ---------------------------------------------------


class KanbanActiveWorker(ResponseModel):
    """``list_active_workers`` SQL row (open run with a ``worker_pid`` on a running task)."""

    run_id: int
    task_id: str
    task_title: str
    task_status: str
    task_assignee: str | None
    profile: str | None
    worker_pid: int
    started_at: int
    claim_lock: str | None
    claim_expires: int | None
    last_heartbeat_at: int | None
    max_runtime_seconds: int | None


class KanbanActiveWorkersResponse(ResponseModel):
    """``plugin_api.list_active_workers``."""

    workers: list[KanbanActiveWorker]
    count: int
    checked_at: int


class KanbanRunResponse(ResponseModel):
    """``plugin_api.get_run_endpoint``."""

    run: KanbanRun


class KanbanRunInspectResponse(ResponseModel):
    """``plugin_api.inspect_run_endpoint`` — the union of the dead (``reason``), live (psutil
    stats) and access-denied (``error``) shapes."""

    run_id: int
    alive: bool
    reason: str | None = None
    pid: int | None = None
    error: str | None = None
    cpu_percent: float | None = None
    memory_rss_bytes: int | None = None
    memory_vms_bytes: int | None = None
    num_threads: int | None = None
    num_fds: int | None = None
    status: str | None = None
    create_time: float | None = None
    cmdline: list[str] | None = None


class KanbanRunTerminateResponse(ResponseModel):
    """``plugin_api.terminate_run_endpoint``."""

    ok: bool
    run_id: int
    task_id: str


class KanbanTaskAckResponse(ResponseModel):
    """``plugin_api.reclaim_task_endpoint``."""

    ok: bool
    task_id: str


class KanbanReassignResponse(ResponseModel):
    """``plugin_api.reassign_task_endpoint``; ``assignee`` is ``None`` when unassigned."""

    ok: bool
    task_id: str
    assignee: str | None


class KanbanSpecifyResponse(ResponseModel):
    """``plugin_api.specify_task_endpoint`` (``kanban_specify.SpecifyOutcome``); non-OK is 200."""

    ok: bool
    task_id: str
    reason: str
    new_title: str | None


class KanbanDecomposeResponse(ResponseModel):
    """``plugin_api.decompose_task_endpoint`` (``kanban_decompose.DecomposeOutcome``); non-OK is 200."""

    ok: bool
    task_id: str
    reason: str
    fanout: bool
    child_ids: list[str]
    new_title: str | None


class KanbanEstimateResponse(ResponseModel):
    """``plugin_api._run_estimate``: ``{ok: false, reason}`` or the parsed estimate."""

    ok: bool
    reason: str | None = None
    est_tokens: int | None = None
    complexity: Literal["S", "M", "L"] | None = None
    rationale: str | None = None
    model: str | None = None


# --- Config / home channels / stats / log / dispatch ----------------------------


class KanbanDashboardConfigResponse(ResponseModel):
    """``plugin_api.get_config`` — the ``dashboard.kanban`` config section with defaults."""

    default_tenant: str
    lane_by_profile: bool
    include_archived_by_default: bool
    render_markdown: bool


class KanbanHomeChannelState(KanbanHomeChannel):
    subscribed: bool


class KanbanHomeChannelsResponse(ResponseModel):
    """``plugin_api.get_home_channels``."""

    home_channels: list[KanbanHomeChannelState]


class KanbanHomeSubscriptionResponse(ResponseModel):
    """``plugin_api.subscribe_home`` / ``unsubscribe_home``."""

    ok: bool
    task_id: str
    home_channel: KanbanHomeChannel


class KanbanStatsResponse(ResponseModel):
    """``kanban_db.board_stats`` — non-archived counts ``{status: n}`` / ``{assignee: {status: n}}``."""

    by_status: dict[str, int]
    by_assignee: dict[str, dict[str, int]]
    oldest_ready_age_seconds: int | None
    now: int


class KanbanAssignee(ResponseModel):
    """``kanban_db.known_assignees`` row."""

    name: str
    on_disk: bool
    counts: dict[str, int]


class KanbanAssigneesResponse(ResponseModel):
    """``plugin_api.get_assignees``."""

    assignees: list[KanbanAssignee]


class KanbanTaskLogResponse(ResponseModel):
    """``plugin_api.get_task_log``; ``content`` is ``""`` when the log does not exist."""

    task_id: str
    path: str
    exists: bool
    size_bytes: int
    content: str
    truncated: bool


class KanbanDispatchResponse(ResponseModel):
    """``asdict(kanban_db_dispatch.DispatchResult)`` from ``plugin_api.dispatch``."""

    reclaimed: int
    promoted: int
    reconciled_orphans: list[str]
    reaped_terminal_workers: list[str]
    spawned: list[tuple[str, str, str]]
    skipped_unassigned: list[str]
    auto_assigned_default: list[str]
    skipped_nonspawnable: list[str]
    skipped_per_profile_capped: list[tuple[str, str, int]]
    crashed: list[str]
    auto_blocked: list[str]
    timed_out: list[str]
    stale: list[str]
    respawn_guarded: list[tuple[str, str]]
    rate_limited: list[str]
    skipped_locked: bool
    memory_pressure: Literal["critical", "elevated"] | None


class KanbanModelOptionProvider(ResponseModel):
    slug: str
    label: str
    models: list[str]


class KanbanModelOptionsResponse(ResponseModel):
    """``plugin_api.model_options``; ``providers`` is ``[]`` when the catalog fails to load."""

    providers: list[KanbanModelOptionProvider]


# --- Projects / boards ------------------------------------------------------------


class KanbanProject(ResponseModel):
    """``plugin_api.list_kanban_projects`` row; empty strings for unset fields."""

    id: str
    slug: str
    name: str
    primary_path: str
    icon: str
    color: str


class KanbanProjectsResponse(ResponseModel):
    """``plugin_api.list_kanban_projects``."""

    projects: list[KanbanProject]


class KanbanBoardListResponse(ResponseModel):
    """``plugin_api.list_boards``."""

    boards: list[KanbanBoardListRow]
    current: str


class KanbanBoardCreateResponse(ResponseModel):
    """``plugin_api.create_board_endpoint``."""

    board: KanbanBoard
    current: str


class KanbanBoardUpdateResponse(ResponseModel):
    """``plugin_api.rename_board``."""

    board: KanbanBoard


class KanbanBoardRemoval(ResponseModel):
    """``kanban_db.remove_board``; ``new_path`` is ``""`` for a hard delete."""

    slug: str
    action: Literal["archived", "deleted"]
    new_path: str


class KanbanBoardDeleteResponse(ResponseModel):
    """``plugin_api.delete_board``."""

    result: KanbanBoardRemoval
    current: str


class KanbanBoardExportResponse(ResponseModel):
    """``kanban_transfer.export_board``; ``counts`` = per-table rows + ``attachment_files`` /
    ``log_files``."""

    board: str
    archive: str
    size: int
    counts: dict[str, int]


class KanbanBoardImportSource(ResponseModel):
    """Read from the archive's ``manifest.json``; absent keys come back ``null``."""

    board: str | None
    exported_at: int | None
    hermes_version: str | None


class KanbanBoardImportResponse(ResponseModel):
    """``kanban_transfer.import_board`` plus the active board slug."""

    board: str
    requested_board: str
    renamed: bool
    name: str
    path: str
    db_path: str
    source: KanbanBoardImportSource
    counts: dict[str, int]
    attachments_restored: int
    tasks_parked: int
    warnings: list[str]
    activated: bool
    current: str


class KanbanBoardSwitchResponse(ResponseModel):
    """``plugin_api.switch_board``."""

    current: str


# --- Profiles / orchestration ------------------------------------------------------


class KanbanProfile(ResponseModel):
    """``plugin_api.list_profile_roster`` row; empty strings for unset fields."""

    name: str
    is_default: bool
    model: str
    provider: str
    description: str
    description_auto: bool
    skill_count: int


class KanbanProfilesResponse(ResponseModel):
    """``plugin_api.list_profile_roster``."""

    profiles: list[KanbanProfile]


class KanbanProfileDescriptionResponse(ResponseModel):
    """``plugin_api.update_profile_description``; ``profile`` is the canonical name."""

    ok: bool
    profile: str
    description: str


class KanbanProfileAutoDescribeResponse(ResponseModel):
    """``plugin_api.auto_describe_profile`` (``profile_describer.DescribeOutcome``); non-OK is 200."""

    ok: bool
    profile: str
    reason: str
    description: str | None


class KanbanWorkflowColumn(ResponseModel):
    """One ``kanban_workflow.Column``: board order is list order."""

    key: str
    label: str
    icon: str
    drag_target: bool


class KanbanWorkflowResponse(ResponseModel):
    """``plugin_api.get_workflow``: ``kanban_workflow.Workflow.to_dict()`` of the default workflow.
    ``manual`` maps a source column key (or ``archived``) to the column keys a human may move to."""

    columns: list[KanbanWorkflowColumn]
    manual: dict[str, list[str]]
    archived: Literal["archived"]


class KanbanOrchestrationResponse(ResponseModel):
    """``plugin_api.get_orchestration_settings`` (PUT returns the same); an unset profile is
    ``""`` while its ``resolved_*`` twin falls back to ``active_profile``."""

    orchestrator_profile: str
    default_assignee: str
    auto_decompose: bool
    auto_promote_children: bool
    resolved_orchestrator_profile: str
    resolved_default_assignee: str
    active_profile: str
