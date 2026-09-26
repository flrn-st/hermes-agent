"""Response contracts for ``hermes_cli/web_routers/profiles.py``."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from hermes_cli.web_responses.base import JsonValue, ResponseModel
from hermes_cli.web_responses.sessions import SessionListRow


class ProfileReadError(ResponseModel):
    """One profile whose ``state.db`` read failed (``_read_profile_db``)."""

    profile: str
    error: str


# ``_corrupt_profile_stores``: profile -> "corrupt" for every scanned store latched unreadable.
ProfileStorageMap = dict[str, Literal["corrupt"]]


class ProfileSessionsResponse(ResponseModel):
    """``get_profiles_sessions`` — rows from every profile's store, tagged with their owner."""

    sessions: list[SessionListRow]
    total: int
    profile_totals: dict[str, int]
    limit: int
    offset: int
    errors: list[ProfileReadError]
    storage: ProfileStorageMap


class ProfileSidebarUsage(ResponseModel):
    """``SessionDB.usage_totals``."""

    tokens: int
    cost_usd: float


class ProfileFailedLoad(ResponseModel):
    """``_profiles_failed``: a profile whose scan failed while its siblings listed (Retry-able)."""

    failed: bool
    retry: bool
    error: str


class ProfileSidebarSlice(ResponseModel):
    """A sidebar slice. When the requested scope's scan failed it is a failed load
    (``_failed_load_slice``): ``failed``/``retry``/``errors`` and NO ``sessions`` — an empty list
    would read as a successful empty read. ``profiles_failed``/``errors`` also mark a sibling
    profile that failed while others listed."""

    sessions: list[SessionListRow] | None = None
    failed: bool | None = None
    retry: bool | None = None
    errors: list[ProfileReadError] | None = None
    profiles_failed: dict[str, ProfileFailedLoad] | None = None


class ProfileSidebarRecents(ProfileSidebarSlice):
    profiles_truncated: dict[str, bool]
    profiles_usage: dict[str, ProfileSidebarUsage]


class ProfileSidebarMessaging(ProfileSidebarSlice):
    total: int


class ProfileSessionsSidebarResponse(ResponseModel):
    """``get_profiles_sessions_sidebar`` — the recents / cron / messaging slices in one scan."""

    recents: ProfileSidebarRecents
    cron: ProfileSidebarSlice
    messaging: ProfileSidebarMessaging
    errors: list[ProfileReadError]
    storage: ProfileStorageMap
    profiles_failed: dict[str, ProfileFailedLoad] | None = None


class ProfileProjectTreeSession(ResponseModel):
    """``tui_gateway/methods_projects.py::_project_tree_row`` stamped by ``_merge_profile_tree``
    (the REST twin of ``ProjectTreeSession`` in ``tui_gateway/contracts/projects_pets.py``)."""

    id: str
    lineage_root_id: str | None = Field(alias="_lineage_root_id")
    lineage_ids: list[str] | None = Field(alias="_lineage_ids")
    parent_session_id: str | None
    reset_from: str | None = Field(alias="_reset_from", description="Set on a /new sibling (not a fork).")
    branched_from: str | None = Field(alias="_branched_from", description="Set on a /branch fork.")
    title: str | None
    preview: str
    started_at: float
    ended_at: float | None
    last_active: float
    source: str
    archived: bool
    message_count: int
    tool_call_count: int
    input_tokens: int
    output_tokens: int
    actual_cost_usd: float | None
    estimated_cost_usd: float | None
    model: str | None
    is_active: bool
    cwd: str | None
    git_branch: str | None
    git_repo_root: str | None
    profile: str
    is_default_profile: bool


class ProfileProjectTreeLane(ResponseModel):
    """One lane of ``tui_gateway/project_tree.py::_build_repos``; ``sessions`` stays empty (the
    all-profiles tree is built unhydrated)."""

    id: str
    label: str
    path: str | None
    isMain: bool
    isKanban: bool
    isGit: bool = Field(True, description="False for a path-only lane of a non-git folder (no branch "
                        "switching); absent on the Home lane.")
    sessions: list[ProfileProjectTreeSession]


class ProfileProjectTreeRepo(ResponseModel):
    """``tui_gateway/project_tree.py::_repo_node``."""

    id: str
    label: str
    path: str | None
    groups: list[ProfileProjectTreeLane]
    sessionCount: int


class ProfileProjectTreeNode(ResponseModel):
    """``tui_gateway/project_tree.py::_project_node`` after ``_merge_profile_tree`` folded the
    same folder across profiles (counts and totals summed)."""

    id: str
    label: str
    path: str | None
    color: str | None
    icon: str | None
    isAuto: bool
    isNoProject: bool
    sessionCount: int
    lastActive: float
    totalTokens: int
    totalCostUsd: float
    repos: list[ProfileProjectTreeRepo]
    previewSessions: list[ProfileProjectTreeSession]
    sessionIds: list[str]
    mergeKey: str = Field(description="The folder identity the merge keyed on (``project_tree._path_key``); a "
                                      "client merging per-profile reads (``?profile=``) folds on it.")


class ProfileProjectsTreeResponse(ResponseModel):
    """``get_profiles_projects_tree`` — the ``projects.tree`` JSON-RPC result
    (``ProjectsTreeResult``) across every profile (or only ``?profile=``), plus per-profile read
    ``errors``."""

    projects: list[ProfileProjectTreeNode]
    active_id: None
    scoped_session_ids: list[str]
    errors: list[ProfileReadError]


class ProfileSessionPullRequest(ResponseModel):
    number: int
    url: str


class ProfileSessionPullRequestsResponse(ResponseModel):
    """``post_profiles_sessions_pull_requests`` — session id -> the PR its transcript opened."""

    pull_requests: dict[str, ProfileSessionPullRequest]
    scanned: list[str]


class ProfileSummary(ResponseModel):
    """``_profile_to_dict``, or ``web_server_profiles.py::_fallback_profile_entry`` when
    ``list_profiles`` fails (that scan omits ``display_name``)."""

    name: str
    path: str
    is_default: bool
    model: str | None
    provider: str | None
    has_env: bool
    skill_count: int
    gateway_running: bool
    description: str
    description_auto: bool
    bot_title: str
    distribution_name: str | None
    distribution_version: str | None
    distribution_source: str | None
    has_alias: bool
    display_name: str | None = None


class ProfileListResponse(ResponseModel):
    """``list_profiles_endpoint`` (``_read_profiles``)."""

    profiles: list[ProfileSummary]


class ProfileHubInstall(ResponseModel):
    """A spawned ``hermes skills install``; ``pid`` is null when the spawn failed."""

    identifier: str
    pid: int | None


class ProfileCreateResponse(ResponseModel):
    """``create_profile_endpoint``; ``model_error`` is ``""`` unless the model pick was rejected."""

    ok: bool
    name: str
    path: str
    model_set: bool
    model_error: str
    mcp_written: int
    skills_disabled: int
    hub_installs: list[ProfileHubInstall]
    soul_set: bool = Field(description="The request carried a ``soul`` (SOUL.md) for the new profile.")


class ProfileActiveResponse(ResponseModel):
    """``get_active_profile_endpoint``: the sticky default and the profile this dashboard serves."""

    active: str
    current: str


class ProfileSetActiveResponse(ResponseModel):
    """``set_active_profile_endpoint``."""

    ok: bool
    active: str


class ProfileSetupCommandResponse(ResponseModel):
    """``get_profile_setup_command``."""

    command: str


class ProfileOpenTerminalResponse(ResponseModel):
    """``open_profile_terminal_endpoint``."""

    ok: bool
    command: str


class ProfileRenameResponse(ResponseModel):
    """``rename_profile_endpoint``; renaming ``default`` only sets ``display_name`` and keeps
    ``name: "default"``."""

    ok: bool
    name: str
    path: str
    display_name: str | None = None


class ProfileDeleteResponse(ResponseModel):
    """``delete_profile_endpoint``; the settlement keys ride only when the directory is gone but
    ``ProfileIdentitySettlementPending`` left its identity unsettled."""

    ok: bool
    path: str
    identity_settled: bool | None = None
    settlement_pending: bool | None = None
    retry_command: str | None = None


class ProfileSoulResponse(ResponseModel):
    """``get_profile_soul``; a missing SOUL.md is ``content: ""``, ``exists: false``."""

    content: str
    exists: bool


class ProfileDescriptionResponse(ResponseModel):
    """``update_profile_description_endpoint``."""

    ok: bool
    description: str
    description_auto: bool


class ProfileModelResponse(ResponseModel):
    """``update_profile_model_endpoint``."""

    ok: bool
    provider: str
    model: str


class ProfileDescribeAutoResponse(ResponseModel):
    """``describe_profile_auto_endpoint`` over ``hermes_cli/profile_describer.py::DescribeOutcome``;
    a failed generation is ``ok: false`` with its ``reason``."""

    ok: bool
    reason: str
    description: str | None
    description_auto: bool


class ProfileExportResponse(ResponseModel):
    """``export_profile_endpoint``."""

    ok: bool
    archive: str


class ProfileImportResponse(ResponseModel):
    """``import_profile_endpoint``; ``desktop`` is the bundled ``desktop.json`` document, null when
    absent or unreadable."""

    ok: bool
    name: str
    path: str
    desktop: JsonValue


class ProfileDesktopOverlayResponse(ResponseModel):
    """``get_profile_desktop_overlay``; ``desktop`` is the file's JSON document (which may itself
    be ``null``)."""

    exists: bool
    desktop: JsonValue
