"""Response contracts for ``hermes_cli/web_routers/cron.py``."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from hermes_cli.web_responses.base import JsonValue, OpenModel, ResponseModel
from hermes_cli.web_responses.sessions import SessionColumns


class CronJobSchedule(OpenModel):
    """``cron/jobs.py::parse_schedule``; open because hand-edited/legacy records may carry other
    keys (``_schedule_display_for_job`` still reads a legacy ``value``)."""

    kind: Literal["once", "interval", "cron"]
    display: str | None = None
    minutes: int | None = None
    expr: str | None = None
    run_at: str | None = None


class CronJobRepeat(ResponseModel):
    times: int | None = Field(description="None = forever.")
    completed: int


class CronJobMonitorState(ResponseModel):
    """``cron/monitor.py::_persist_monitor_state``."""

    last_output_hash: str
    last_changed_at: str


class CronJobFireError(ResponseModel):
    """``cron/jobs.py::note_fire_forward_failure``."""

    at: str
    detail: str


class CronJobExecution(ResponseModel):
    """One ``executions`` row of ``cron/executions.db`` (``cron/executions.py::latest_executions``)."""

    id: str
    job_id: str
    source: str
    process_id: str
    pid: int
    process_started_at: int | None
    status: Literal["claimed", "running", "completed", "failed", "unknown"]
    handoff_pending: int
    handoff_started_at: float | None
    claimed_at: str
    progress_at: str | None = Field(description="Last liveness stamp of a running attempt; staleness counts from it.")
    started_at: str | None
    finished_at: str | None
    error: str | None
    delivery_outcome: str | None
    scheduled_instant: str | None


class CronJob(OpenModel):
    """One ``jobs.json`` record as the dashboard sees it: ``cron/jobs.py::create_job`` fields
    (read paths go through ``_normalize_job_record``) plus the profile annotation of
    ``hermes_cli/web_server_cron.py::_annotate_cron_job``.

    Open because the scheduler stamps bookkeeping keys onto the record (``run_claim``,
    ``fire_claim``, ``pending_slot``, ``preflight_alerted``, quota-hold state, ...). Keys that
    ``create_job`` always writes are still optional here: legacy/hand-edited records may predate
    them, and readers fall back (``enabled`` defaults to true)."""

    id: str
    name: str
    prompt: str
    skills: list[str]
    skill: str | None = Field(description="Legacy single-skill alias: the first of ``skills``.")
    schedule: CronJobSchedule
    schedule_display: str
    state: str = Field(description='Effective state; "scheduled", "paused", "completed" or "error".')

    model: str | None = None
    provider: str | None = None
    base_url: str | None = None
    script: str | None = None
    no_agent: bool = False
    monitor_script: str | None = None
    monitor_url: str | None = None
    monitor_state: CronJobMonitorState | None = None
    context_from: list[str] | None = None
    repeat: CronJobRepeat | None = None
    enabled: bool = True
    paused_at: str | None = None
    paused_reason: str | None = None
    created_at: str | None = None
    next_run_at: str | None = None
    last_run_at: str | None = None
    last_status: str | None = None
    last_error: str | None = None
    last_delivery_error: str | None = None
    last_delivery_unverified: list[str] | None = Field(
        None, description="``platform:chat_id`` targets acked without delivery evidence.")
    failure_streak: int = 0
    deliver: str | None = None
    origin: dict[str, JsonValue] | None = None
    enabled_toolsets: list[str] | None = None
    workdir: str | None = None
    # Persisted only when explicitly set.
    attach_to_session: bool | None = None
    reasoning_effort: str | None = None
    failure_deliver: str | None = None
    manual_run_at: str | None = None
    manual_run_prompt: str | None = None
    last_fire_error: CronJobFireError | None = None
    last_failure: CronJobFireError | None = Field(
        None, description="The latest failed run (cleared by a success); kept apart from ``last_status``.")
    interpreter: str | None = Field(None, description="Python for a ``.py`` script/monitor_script.")
    canonical_completions: list[str] | None = Field(
        None, description="Execution ids whose completion is already recorded (``mark_job_run``); a replay is a no-op.")
    latest_execution: CronJobExecution | None = Field(
        None, description="Only on list rows (``cron/jobs.py::list_jobs``); null when never executed.")

    profile: str
    profile_name: str
    hermes_home: str
    is_default_profile: bool
    scheduler_heartbeat_age_s: float | None = Field(
        description="Seconds since the profile's ticker last iterated; null when never/unknown.")


class CronJobRunSession(SessionColumns):
    """One ``SessionDB.list_cron_job_runs`` row (the ``list_sessions_rich`` shape, compression
    lineage skipped) annotated by ``_list_cron_job_runs_sync``: ``archived`` becomes a bool,
    ``pinned`` stays SQLite 0/1."""

    archived: bool
    pinned: int
    preview: str
    last_active: float
    is_active: bool
    scheduler_owned: bool = Field(
        description="The scheduler still owns this run (``_run_owned_by``): live even past the activity window.")
    stored_model_config: str | None = Field(alias="model_config")
    system_prompt: str | None
    system_prompt_hash: str | None
    git_metadata_generation: int
    profile: str | None = Field(None, description="Absent when no profile holds the job.")


class CronJobOutputRun(ResponseModel):
    """``_cron_output_run_row``: an execution with no session (a script-only fire, or one whose
    session is gone), built from its output doc, the execution ledger or ``last_run_at``."""

    id: str = Field(description='"cron_output:<job>:<doc stem>", "…:exec:<n>" or "…:latest".')
    title: str
    preview: str | None
    source: Literal["cron_output"]
    started_at: float
    last_active: float
    ended_at: float
    input_tokens: int
    output_tokens: int
    message_count: int
    tool_call_count: int
    model: None
    cwd: None
    archived: bool
    is_active: bool


class CronJobRunsResponse(ResponseModel):
    """``_list_cron_job_runs_sync`` — run sessions merged with output-doc rows for executions no
    session represents (``_reconcile_cron_runs``), newest first."""

    runs: list[CronJobRunSession | CronJobOutputRun]
    limit: int


class CronDeliveryTarget(ResponseModel):
    """``cron/scheduler_delivery.py::cron_delivery_targets`` (plus the implicit ``local`` row)."""

    id: str
    name: str
    home_target_set: bool
    home_env_var: str | None


class CronDeliveryTargetsResponse(ResponseModel):
    """``get_cron_delivery_targets``."""

    targets: list[CronDeliveryTarget]


class CronBlueprintField(ResponseModel):
    """One ``cron/blueprint_catalog.py::BlueprintSlot`` as a form field."""

    name: str
    type: Literal["time", "enum", "text", "weekdays"]
    label: str
    default: str | None
    options: list[str]
    optional: bool
    strict: bool = Field(description="False: ``options`` are suggestions, any value is accepted.")
    help: str


class CronBlueprint(ResponseModel):
    """``cron/blueprint_catalog.py::blueprint_catalog_entry``: built-ins, plus the profile's plugin
    blueprints (``key`` is ``<plugin>:<key>``)."""

    key: str
    source: Literal["builtin", "plugin"]
    plugin: str | None = Field(description="The registering plugin; null for a built-in.")
    title: str
    description: str
    category: str
    tags: list[str]
    fields: list[CronBlueprintField]
    schedule: str = Field(description="Cron expression template with ``{slot}`` placeholders.")
    scheduleHuman: str
    command: str = Field(description="Ready-to-paste ``/blueprint`` slash command.")
    appUrl: str = Field(description="``hermes://blueprint/...`` deep link.")


class CronBlueprintsResponse(ResponseModel):
    """``list_cron_blueprints``."""

    blueprints: list[CronBlueprint]


class CronFireResponse(ResponseModel):
    """``cron_fire_webhook`` success: its own ``gone``/``gateway_stopped`` answers, or the
    gateway api_server's (``gateway/platforms/api_server.py::_handle_cron_fire``) passed through:
    ``accepted`` (202) or ``duplicate`` (200)."""

    status: str = Field(description='"gone", "gateway_stopped", "duplicate" or "accepted".')
    job_id: str
    detail: str | None = None
    profile: str | None = None


class CronFireErrorResponse(ResponseModel):
    """``cron_fire_webhook`` rejections (401 bad token, 400 missing ``job_id``, 503 gateway
    unreachable) and the gateway's own error bodies passed through (draining uses the OpenAI
    error object). A non-JSON gateway body arrives wrapped as ``raw``."""

    error: str | dict[str, JsonValue] | None = None
    raw: JsonValue = None
    job_id: str | None = None
    profile: str | None = None
