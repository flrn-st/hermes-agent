"""Response contracts for ``hermes_cli/web_routers/actions.py`` (``router`` + ``status_router``)."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from hermes_cli.web_responses.base import JsonValue, OpenModel, ResponseModel


class GatewayMigrationService(ResponseModel):
    """``hermes_cli/gateway_migrate.py::_service_dict`` — ``kind`` is ``systemd``, ``launchd``,
    ``s6`` or ``windows``; ``system`` marks a system-scope systemd unit."""

    kind: str
    system: bool


class GatewayMigrationProfile(ResponseModel):
    """``hermes_cli/gateway_migrate.py::ProfileGateway.to_dict``."""

    profile: str
    home: str
    pid: int | None
    service: GatewayMigrationService | None
    services: list[GatewayMigrationService]
    run_as_user: str | None
    uid: int | None
    runtime_home: str | None


class GatewayMigrationPlanResponse(ResponseModel):
    """``gateway_migrate_plan`` → ``hermes_cli/gateway_migrate.py::MigrationPlan.to_dict`` (the
    same JSON as ``hermes gateway migrate --plan``)."""

    default_home: str
    profiles: list[GatewayMigrationProfile]
    standalone_by_config: list[str]
    multiplex_flag_on: bool
    live_served: list[str] | None
    already_multiplexed: bool
    interrupted: bool
    blockers: list[str]
    notices: list[str]
    eligible: bool
    command: str


class GatewayDrainResponse(ResponseModel):
    """``gateway_drain``: ``cancel`` answers ``was_draining``; ``drain`` echoes the marker it wrote
    (``gateway/drain_control.py::write_drain_request``) and whether a drain is now active."""

    ok: bool
    action: Literal["drain", "cancel"]
    was_draining: bool | None = None
    requested_at: str | None = None
    draining: bool | None = None
    suppress_notification: bool | None = None


class HermesUpdateStartResponse(ResponseModel):
    """``update_hermes``: a refusal (``ok: false`` + ``error``/``message``/``update_command``,
    via ``_update_refused``), the already-running update, or the freshly spawned one."""

    ok: bool
    pid: int | None
    name: str
    error: str | None = None
    message: str | None = None
    update_command: str | None = None
    already_running: bool | None = None
    action_id: str | None = None


class HermesUpdateCommit(ResponseModel):
    """``hermes_cli/source_check.py::_commits`` row, reshaped by ``check_hermes_update``: ``sha``
    shortened to 7 chars, ``at`` in epoch seconds."""

    sha: str
    summary: str
    author: str
    at: int


class HermesUpdateCheckResponse(ResponseModel):
    """``check_hermes_update``. ``behind``: commits behind, ``0`` up to date, ``-1`` behind by an
    unknown count, ``null`` when the check could not run or does not apply. ``commits`` only when
    an update is available, together with ``channel`` / ``branch`` / ``source_version`` (the release
    channel and release that pick its notes source; each null when the source check names none);
    ``rollback_to`` only when that "update" is a stable release older than this build."""

    install_method: str
    current_version: str
    behind: int | None
    update_available: bool
    can_apply: bool
    update_command: str
    message: str | None
    rollback_to: str | None = None
    channel: str | None = None
    branch: str | None = None
    source_version: str | None = None
    commits: list[HermesUpdateCommit] | None = None


class UpdateFollowup(ResponseModel):
    """A post-commit step a committed update still owes (``update_receipt`` follow-up)."""

    step: str
    reason: str


class UpdateUserAction(OpenModel):
    """``update_receipt.record_user_action``: something only the user can do is still owed; copied
    from the receipt file as stored."""

    step: str
    reason: str


class UpdateReceiptSummary(ResponseModel):
    """``_latest_update_receipt_summary``; values are copied out of the receipt file, so any may be
    ``null`` when that receipt lacks them. ``action_id`` names the run the receipt belongs to."""

    outcome: str | None
    started_at: str | None
    finished_at: str | None
    action_id: str | None
    pre_sha: str | None
    post_sha: str | None
    post_version: str | None
    fleet_states: list[str]
    followups: list[UpdateFollowup]
    user_action: UpdateUserAction | None


class ActionStatusResponse(ResponseModel):
    """``get_action_status``; ``action_id`` and ``receipt`` only for ``hermes-update``."""

    name: str
    running: bool
    exit_code: int | None
    pid: int | None
    lines: list[str]
    action_id: str | None = None
    receipt: UpdateReceiptSummary | None = None


class UpdateReceiptStep(OpenModel):
    """``hermes_cli/update_receipt.py::UpdateReceipt.step``."""

    name: str
    ok: bool
    detail: str
    at: str


class UpdateReceiptSkip(OpenModel):
    """``hermes_cli/update_receipt.py::UpdateReceipt.skip``."""

    name: str
    reason: str
    at: str


class UpdateReceiptRecord(OpenModel):
    """``latest.json`` as ``hermes_cli/update_receipt.py`` wrote it, returned verbatim. The file
    outlives the code that wrote it, so every key may be absent; ``finalize_update_receipt`` also
    embeds ``pm_*`` sync sections, ``update_cmd_fleet`` adds ``runtime_outcomes``."""

    schema_: int | None = Field(default=None, alias="schema")
    update_id: str | None = None
    started_at: str | None = None
    finished_at: str | None = None
    argv: list[str] | None = None
    pid: int | None = None
    outcome: str | None = None
    pre_update: dict[str, JsonValue] | None = None
    post_update: dict[str, JsonValue] | None = None
    steps: list[UpdateReceiptStep] | None = None
    skips: list[UpdateReceiptSkip] | None = None
    gateway_restart: dict[str, JsonValue] | None = None
    fleet: list[dict[str, JsonValue]] | None = None
    stop_reason: str | None = None
    exit_code: int | None = None
    plan: dict[str, JsonValue] | None = None
    pending_manual_serves: list[dict[str, JsonValue]] | None = None


class UpdateReceiptResponse(ResponseModel):
    """``get_update_receipt``: the full latest receipt plus its compact summary."""

    receipt: UpdateReceiptRecord
    summary: UpdateReceiptSummary | None
