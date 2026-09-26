"""Response contracts for ``hermes_cli/web_routers/git.py``.

Every payload is built in ``hermes_cli/web_git.py`` (the remote mirror of the desktop's
Electron-local git ops), so keys travel camelCase where the Electron shapes do.
"""

from __future__ import annotations

from hermes_cli.web_responses.base import ResponseModel


class GitStatusFile(ResponseModel):
    """``web_git._classify``."""

    path: str
    staged: bool
    unstaged: bool
    untracked: bool
    conflicted: bool


class GitRepoStatusResponse(ResponseModel):
    """``web_git.repo_status`` (the route answers ``null`` for a non-repo). The four flag
    counters and ``changed`` cover every file; ``files`` is capped at 200."""

    branch: str | None
    defaultBranch: str | None
    detached: bool
    ahead: int
    behind: int
    staged: int
    unstaged: int
    untracked: int
    conflicted: int
    changed: int
    added: int
    removed: int
    files: list[GitStatusFile]


class GitHubCliAuthResponse(ResponseModel):
    """``git._probe_gh_auth`` (cached 5 min by ``gh_auth_status_route``)."""

    available: bool
    authenticated: bool


class GitWorktreeRow(ResponseModel):
    """``web_git.worktree_list`` row; the main tree comes first."""

    path: str
    branch: str | None
    isMain: bool
    detached: bool
    locked: bool


class GitWorktreesResponse(ResponseModel):
    """``git_worktrees_route``."""

    worktrees: list[GitWorktreeRow]


class GitBranchRow(ResponseModel):
    """``web_git.branch_list`` row: local heads, then remote-tracking refs without a local head."""

    name: str
    checkedOut: bool
    isDefault: bool
    isRemote: bool
    worktreePath: str | None


class GitBranchesResponse(ResponseModel):
    """``git_branches_route``."""

    branches: list[GitBranchRow]


class GitBaseBranchRow(ResponseModel):
    """``web_git.base_branch_list`` row."""

    name: str
    isRemote: bool
    isDefault: bool


class GitBaseBranchesResponse(ResponseModel):
    """``git_base_branches_route``."""

    branches: list[GitBaseBranchRow]


class GitReviewFile(ResponseModel):
    """``web_git.review_list`` row. ``status`` is ``"?"`` (untracked), ``"U"`` (conflicted) or
    git's index/worktree code letter (``M``, ``A``, ``D``, ``R``, ...)."""

    path: str
    added: int
    removed: int
    status: str
    staged: bool


class GitReviewListResponse(ResponseModel):
    """``web_git.review_list``; ``base`` is the resolved base ref for the branch/lastTurn scopes."""

    files: list[GitReviewFile]
    base: str | None


class GitDiffResponse(ResponseModel):
    """``git_review_diff_route`` / ``git_file_diff_route``: unified diff text (``""`` when none)."""

    diff: str


class GitCommitContextResponse(ResponseModel):
    """``web_git.review_commit_context`` — the diff that will commit plus recent subjects."""

    diff: str
    recent: str


class GitRevParseResponse(ResponseModel):
    """``git_rev_parse_route``; ``null`` when the ref does not resolve."""

    sha: str | None


class GitShipInfoPr(ResponseModel):
    """The ``gh pr view --json url,state,number`` fields ``web_git.review_ship_info`` keeps."""

    url: str
    state: str | None
    number: int | None


class GitShipInfoResponse(ResponseModel):
    """``web_git.review_ship_info``."""

    ghReady: bool
    pr: GitShipInfoPr | None


class GitPullRequestRow(ResponseModel):
    """``web_git._pr_payload``; ``state`` is GitHub's PR state lowercased."""

    branch: str
    draft: bool
    number: int
    state: str
    title: str
    url: str


class GitPrListResponse(ResponseModel):
    """``web_git.review_pr_list``."""

    ghReady: bool
    prs: list[GitPullRequestRow]


class GitCreatePrResponse(ResponseModel):
    """``web_git.review_create_pr`` — the last non-empty line ``gh pr create`` printed."""

    url: str


class GitWorktreeAddResponse(ResponseModel):
    """``web_git.worktree_add`` / ``web_git._worktree_for_existing``."""

    path: str
    branch: str
    repoRoot: str


class GitWorktreeRemoveResponse(ResponseModel):
    """``web_git.worktree_remove``."""

    removed: str


class GitBranchSwitchResponse(ResponseModel):
    """``web_git.branch_switch`` — the sanitized branch that was switched to."""

    branch: str
