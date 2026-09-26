"""Response contracts for ``hermes_cli/web_routers/chat_workspaces.py``.

The project and repo rows are the ones the Desktop sidebar reads over JSON-RPC
(``tui_gateway/contracts/projects_pets.py::ProjectInfo`` / ``DiscoveredRepo``).
"""

from __future__ import annotations

from hermes_cli.web_responses.base import ResponseModel


class ChatWorkspaceProjectFolder(ResponseModel):
    """``hermes_cli/projects_db.py::ProjectFolder.to_dict``."""

    path: str
    label: str | None
    is_primary: bool
    added_at: int


class ChatWorkspaceProject(ResponseModel):
    """``hermes_cli/projects_db.py::Project.to_dict`` (the ``projects.list`` row)."""

    id: str
    slug: str
    name: str
    description: str | None
    icon: str | None
    color: str | None
    board_slug: str | None
    primary_path: str | None
    archived: bool
    created_at: int
    folders: list[ChatWorkspaceProjectFolder]


class ChatWorkspaceRepo(ResponseModel):
    """``tui_gateway/methods_projects.py::_discover_repos_payload`` row: a git root with its session
    totals (``last_active`` is an epoch, ``0.0`` for a scanned repo with no sessions)."""

    root: str
    label: str
    sessions: int
    last_active: float


class ChatWorkspacesResponse(ResponseModel):
    """``_collect_workspaces``. ``default_cwd`` is where a chat without ``?cwd=`` starts; ``home``
    is the host user's home directory."""

    projects: list[ChatWorkspaceProject]
    repos: list[ChatWorkspaceRepo]
    default_cwd: str
    home: str
    scan_enabled: bool
