"""Response contracts for ``hermes_cli/web_routers/sessions.py``.

The session and message rows are ``SELECT *`` projections of ``hermes_state_common.py::SCHEMA_SQL``
(``sessions`` / ``messages``) plus computed keys, so they are ``OpenModel``: a store that kept a
column across a schema change still returns it. ``web_responses/profiles.py`` reuses the list row.
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from hermes_cli.web_responses.base import JsonValue, OkResponse, OpenModel, ResponseModel


# ── session rows ────────────────────────────────────────────────────────────────────────────


class SessionColumns(OpenModel):
    """The ``sessions`` columns every session read carries. Counters are ``DEFAULT 0`` and no
    writer binds NULL to them (imports coerce to ``0``). ``tool_names`` is the resolved list text on
    the detail read and the raw column (possibly a ``system_prompts`` hash) on list rows."""

    id: str
    runtime_revision: int = Field(description="Mutation fence: bumped by every committed session mutation.")
    runtime_generation: int = Field(description="Execution generation a turn-affecting mutation must quote.")
    source: str
    created_source: str | None = Field(description="The source the row was created under; null on rows that predate it.")
    user_id: str | None
    session_key: str | None
    chat_id: str | None
    chat_type: str | None
    thread_id: str | None
    display_name: str | None
    origin_json: str | None
    expiry_finalized: int
    model: str | None
    parent_session_id: str | None
    started_at: float
    ended_at: float | None
    end_reason: str | None
    message_count: int
    tool_call_count: int
    input_tokens: int
    output_tokens: int
    cache_read_tokens: int
    cache_write_tokens: int
    reasoning_tokens: int
    cwd: str | None
    git_branch: str | None
    git_repo_root: str | None
    billing_provider: str | None
    billing_base_url: str | None
    billing_mode: str | None
    estimated_cost_usd: float | None
    actual_cost_usd: float | None
    cost_status: str | None
    cost_source: str | None
    pricing_version: str | None
    title: str | None
    title_source: str | None
    last_activity_at: float | None
    last_activity_description: str | None
    last_activity_provenance: str | None
    api_call_count: int
    handoff_state: str | None
    handoff_platform: str | None
    handoff_error: str | None
    compression_failure_cooldown_until: float | None
    compression_failure_error: str | None
    compression_fallback_streak: int
    compression_ineffective_count: int
    compression_recovery_deadline: float | None
    profile_name: str | None
    transport_profile: str | None
    rewind_count: int
    auto_archived: int = Field(description="SQLite 0/1: archived by the idle sweep, not by hand.")
    hidden: int
    last_read_at: float | None = Field(description="Read watermark; ``0`` = marked unread, null = never tracked.")
    tool_names: str | None
    reset_from: str | None = Field(
        None, alias="_reset_from", description="Lifted from ``model_config`` when set: a /new sibling.")
    branched_from: str | None = Field(
        None, alias="_branched_from", description="Lifted from ``model_config`` when set: a /branch fork.")


class SessionListRow(SessionColumns):
    """One ``SessionDB.list_sessions_rich`` row as the list endpoints stamp it (``is_active``,
    ``profile``, boolean ``archived`` / ``pinned``). The prompt-storage columns ride only with
    ``full=1``; the ``_lineage_*`` keys and ``continuation_kind`` only on a compression root projected
    onto its live tip."""

    archived: bool
    pinned: bool
    last_active: float
    preview: str
    unread: bool
    is_active: bool
    profile: str
    is_default_profile: bool
    lineage_root_id: str | None = Field(default=None, alias="_lineage_root_id")
    lineage_ids: list[str] | None = Field(default=None, alias="_lineage_ids")
    continuation_kind: Literal["compression"] | None = Field(
        default=None, description="Only on a compression root projected onto its live tip.")
    stored_model_config: str | None = Field(default=None, alias="model_config")
    system_prompt: str | None = None
    system_prompt_hash: str | None = None
    git_metadata_generation: int | None = None


class SessionStorageRow(SessionColumns):
    """``SessionDB.get_session``: every column, prompt text resolved; flags stay SQLite 0/1."""

    archived: int
    pinned: int
    stored_model_config: str | None = Field(alias="model_config")
    system_prompt: str | None
    system_prompt_hash: str | None
    git_metadata_generation: int


class SessionListResponse(ResponseModel):
    """``get_sessions``. ``storage`` maps the serving profile to ``"corrupt"`` when its store is
    latched unreadable, else ``{}``."""

    sessions: list[SessionListRow]
    total: int
    limit: int
    offset: int
    storage: dict[str, Literal["corrupt"]]


class SessionDetailResponse(SessionStorageRow):
    """``get_session_detail`` — the stored row stamped with its owning profile. A cron run also
    carries ``scheduler_owned`` (``cron.cron_run_scheduler_owned``): its liveness is scheduler
    ownership, not the activity window."""

    profile: str
    is_default_profile: bool
    scheduler_owned: bool | None = None


# ── search ──────────────────────────────────────────────────────────────────────────────────


class SessionSearchResult(ResponseModel):
    """One lineage-deduped hit built by ``search_sessions``. Id matches carry ``role: null``; FTS
    hits carry ``last_active: null`` unless the tip row hydrated. The row fields are present only
    when ``get_session_rich_row`` found the tip."""

    snippet: str
    role: str | None
    source: str | None
    model: str | None
    session_started: float | None
    last_active: float | None
    session_id: str
    lineage_root: str
    profile: str
    is_default_profile: bool
    id: str
    title: str | None = None
    started_at: float | None = None
    ended_at: float | None = None
    is_active: bool | None = None
    message_count: int | None = None
    tool_call_count: int | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    preview: str | None = None
    parent_session_id: str | None = None
    archived: bool | None = None


class SessionSearchResponse(ResponseModel):
    """``search_sessions``."""

    results: list[SessionSearchResult]


# ── mutations / counters ────────────────────────────────────────────────────────────────────


class SessionDeletedCountResponse(ResponseModel):
    """``delete_empty_sessions_endpoint``."""

    ok: bool
    deleted: int


class SessionBulkDeleteResponse(SessionDeletedCountResponse):
    """``bulk_delete_sessions_endpoint``: ``deleted`` counts the selected rows (compression chains are
    deleted whole); ``skipped_active`` lists ids a live turn or compression still owns, which stay."""

    skipped_active: list[str]


class SessionMutationReceipt(ResponseModel):
    """The committed receipt of a fenced session mutation (``web_server_sessions._mutate_session_request``
    → ``hermes_state_runtime.mutate_runtime_session``, or the gateway authority's
    ``gateway/session_mutations.mutate_session``): the session's new ``revision`` and its
    ``execution_generation``, plus the operation's own projection. An exact retry of the same
    ``request_id`` replays the stored receipt."""

    ok: bool
    session_id: str
    revision: int
    execution_generation: int | None


class SessionImportResponse(SessionMutationReceipt):
    """``import_sessions_endpoint``: the receipt of an ``import`` mutation anchored on the payload's
    first session, with ``hermes_state_mutations._import``'s projection (validation failures are a
    400, a conflicting retry a 409)."""

    operation: Literal["import"]
    imported: int
    skipped: int
    detached: int
    imported_ids: list[str]
    skipped_ids: list[str]
    errors: list[dict[str, JsonValue]]


class SessionEmptyCountResponse(ResponseModel):
    """``count_empty_sessions_endpoint``."""

    count: int


class SessionStatsResponse(ResponseModel):
    """``get_session_stats``; ``by_source`` is ``{}`` when the grouped count fails."""

    total: int
    active_store: int
    archived: int
    messages: int
    by_source: dict[str, int]


class SessionLatestDescendantResponse(ResponseModel):
    """``get_session_latest_descendant``."""

    requested_session_id: str
    session_id: str
    path: list[str]
    changed: bool


class SessionDeleteResponse(OkResponse):
    """``delete_session_endpoint``: the ``delete`` mutation receipt (``deleted_ids``: every retired
    row of the compression chain), or ``{ok, already_absent: true}`` when the id is already gone."""

    already_absent: bool | None = None
    session_id: str | None = None
    revision: int | None = None
    execution_generation: int | None = None
    operation: Literal["delete"] | None = None
    deleted_ids: list[str] | None = None


class SessionMutationSnapshotResponse(ResponseModel):
    """``get_session_mutation_snapshot``: the fencing counters a mutation must quote
    (``expected_revision`` / ``expected_generation``). An absent session reads revision ``0`` and
    generation ``null`` (the anchor of an import)."""

    session_id: str
    exists: bool
    runtime_revision: int
    runtime_generation: int | None


class SessionOwnerBackfillResponse(ResponseModel):
    """``backfill_session_owner_profiles``."""

    ok: bool
    stamped: int
    profile: str


class SessionRenameResponse(SessionMutationReceipt):
    """``rename_session_endpoint``: the receipt of a ``sidebar`` mutation. ``title`` (as stored, null
    when cleared) and each flag are echoed only when the request set them."""

    operation: Literal["sidebar"]
    title: str | None = None
    archived: bool | None = None
    hidden: bool | None = None
    pinned: bool | None = None
    unread: bool | None = None


class SessionPruneRow(ResponseModel):
    """``_PRUNE_ROW_KEYS`` of one ``SessionDB.list_prune_candidates`` row."""

    id: str
    source: str
    title: str | None
    model: str | None
    started_at: float
    last_active: float
    message_count: int


class SessionPruneResponse(ResponseModel):
    """``_prune_sessions``: a real prune answers ``ok`` / ``removed`` / ``skipped_open``; a dry run
    adds the preview keys (``removed`` is then ``0``)."""

    ok: bool
    removed: int
    skipped_open: int
    matched: int | None = None
    oldest_last_active: float | None = None
    newest_last_active: float | None = None
    oldest_started_at: float | None = None
    newest_started_at: float | None = None
    sessions: list[SessionPruneRow] | None = None


# ── messages ────────────────────────────────────────────────────────────────────────────────


class SessionMessage(OpenModel):
    """``SessionDB._row_to_message_dict``: a ``messages`` row with ``content`` / ``tool_calls`` /
    ``display_metadata`` decoded and the display-index columns dropped. ``content`` is text or the
    decoded multimodal parts; the reasoning sidecars stay JSON text."""

    id: int
    session_id: str
    role: str
    content: JsonValue
    tool_call_id: str | None
    tool_calls: JsonValue = Field(description="Decoded tool-call list (``[]`` when undecodable), or null.")
    tool_name: str | None
    effect_disposition: str | None
    timestamp: float
    token_count: int | None
    finish_reason: str | None
    reasoning: str | None
    reasoning_content: str | None
    reasoning_details: str | None
    codex_reasoning_items: str | None
    codex_message_items: str | None
    platform_message_id: str | None
    observed: int
    active: int
    compacted: int
    api_content: str | None
    display_kind: str | None
    display_metadata: dict[str, JsonValue] | None
    message_uid: str | None = Field(description="Stable message identity; null on legacy rows until backfilled.")
    absorbed_message_uids: str | None
    tool_call_uids: str | None
    tool_call_uid: str | None
    compressed_summary: bool | None = Field(default=None, alias="_compressed_summary")


class SessionToolCallLabel(ResponseModel):
    """``tools/tool_labels.py::ToolLabel.as_payload`` (twin of the ``ToolLabel`` JSON-RPC payload)."""

    kind: Literal["connector", "mcp", "tool"]
    app: str
    action: str
    emoji: str
    text: str
    name: str
    preview: str


class SessionDisplayMessage(SessionMessage):
    """A message after ``_project_for_display``: bridge tool-call labels, the compaction display
    projection and ``agent/history_commentary.py::_project_one`` keys, each only when it applies.
    A recovered compaction carrier drops ``display_kind`` in favour of ``display_content``."""

    display_kind: str | None = None
    tool_call_labels: dict[str, list[SessionToolCallLabel]] | None = None
    display_content: JsonValue = None
    display_commentary: list[str] | None = None
    display_reasoning: str | None = None


class SessionMessagesPagination(ResponseModel):
    limit: int
    offset: int
    order: Literal["oldest", "latest"]
    returned: int


class SessionMessagesResponse(ResponseModel):
    """``get_session_messages``."""

    session_id: str
    profile: str
    messages: list[SessionDisplayMessage]
    pagination: SessionMessagesPagination


class SessionTimelineEntry(ResponseModel):
    row_id: int
    preview: str
    timestamp: float


class SessionTimelinePagination(ResponseModel):
    limit: int
    after_row_id: int
    returned: int
    total: int
    has_more: bool
    next_cursor: int | None


class SessionTimelineResponse(ResponseModel):
    """``get_session_timeline`` over ``hermes_state_timeline.py::get_session_timeline``."""

    session_id: str
    profile: str
    entries: list[SessionTimelineEntry]
    pagination: SessionTimelinePagination


class SessionMessagesAroundPagination(ResponseModel):
    row_id: int
    limit: int
    returned: int
    order: Literal["oldest"]
    offset: int
    total: int
    has_older: bool
    has_newer: bool


class SessionMessagesAroundResponse(ResponseModel):
    """``get_session_messages_around`` over
    ``hermes_state_timeline.py::get_session_messages_around``."""

    session_id: str
    profile: str
    messages: list[SessionDisplayMessage]
    pagination: SessionMessagesAroundPagination


class SessionExportResponse(SessionStorageRow):
    """``export_session_endpoint`` streams this one JSON document: ``SessionDB.get_session`` with
    every raw (unprojected) message appended."""

    messages: list[SessionMessage]
