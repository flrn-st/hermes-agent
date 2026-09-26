"""Response contracts for ``hermes_cli/web_routers/skills.py`` (``hub_router`` and ``router``)."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from hermes_cli.web_responses.base import OkResponse, ResponseModel

# ── skills hub ────────────────────────────────────────────────────────────────────────────────


class SkillHubEntry(ResponseModel):
    """``_skill_meta_to_payload`` over ``tools/skills_hub_models.py::SkillMeta``."""

    name: str
    description: str
    source: str
    identifier: str
    trust_level: str
    repo: str | None
    tags: list[str]


class SkillHubOfficialEntry(SkillHubEntry):
    """``list_official_skills`` row: ``category`` from ``official/<category>/<skill>``
    (``"general"`` when flat)."""

    category: str
    installed: bool


class SkillHubOfficialResponse(ResponseModel):
    """``list_official_skills`` — the whole optional-skills catalog."""

    skills: list[SkillHubOfficialEntry]


class SkillHubInstalledRecord(ResponseModel):
    """``hermes_cli/web_server_profiles.py::_installed_hub_identifiers`` value — lock-file fields
    read with ``.get`` (``null`` on legacy entries)."""

    name: str
    trust_level: str | None
    scan_verdict: str | None


class SkillHubSource(ResponseModel):
    """``list_skills_hub_sources`` row; ``rate_limited`` only for ``github``, ``available`` only
    for ``hermes-index``."""

    id: str
    label: str
    searchable: bool
    rate_limited: bool | None = None
    available: bool | None = None


class SkillHubSourcesResponse(ResponseModel):
    """``list_skills_hub_sources``; ``installed`` is keyed by hub identifier."""

    sources: list[SkillHubSource]
    index_available: bool
    featured: list[SkillHubEntry]
    installed: dict[str, SkillHubInstalledRecord]


class SkillHubSearchResponse(ResponseModel):
    """``search_skills_hub`` (all-empty for a blank query); ``source_counts`` / ``timed_out``
    come from ``tools/skills_hub_search.py::parallel_search_sources``."""

    results: list[SkillHubEntry]
    source_counts: dict[str, int]
    timed_out: list[str]
    installed: dict[str, SkillHubInstalledRecord]


class SkillHubPreviewResponse(ResponseModel):
    """``preview_skill_hub`` — ``repo`` is ``null`` when only a bundle resolved; ``files`` are
    the bundle's relative paths, sorted."""

    name: str
    description: str
    source: str
    identifier: str
    trust_level: str
    repo: str | None
    tags: list[str]
    skill_md: str
    files: list[str]


class SkillHubScanFinding(ResponseModel):
    """``tools/skills_guard.py::Finding`` subset."""

    severity: str
    category: str
    file: str
    line: int
    description: str


class SkillHubScanSeverityCounts(ResponseModel):
    critical: int
    high: int
    medium: int
    low: int


class SkillHubTier1Finding(ResponseModel):
    """``tools/skillevaluator_scan.py::Tier1Finding``; ``secrets_class`` is ``is_secrets_class``."""

    check: str
    validator: str
    severity: str
    message: str
    file: str
    line: int
    secrets_class: bool


class SkillHubTier1Report(ResponseModel):
    """Advisory SkillEvaluator Tier 1 result (``tools/skillevaluator_scan.py::Tier1Report``)."""

    passed: bool
    incomplete_checks: list[str]
    findings: list[SkillHubTier1Finding]


class SkillHubScanResponse(ResponseModel):
    """``scan_skill_hub`` — ``tools/skills_guard.py::scan_skill`` + ``should_allow_install``
    (``True``/``None``/``False`` → ``allow``/``ask``/``block``). ``tier1`` is ``null`` when the
    optional scanner is not installed or enabled."""

    name: str
    identifier: str
    source: str
    trust_level: str
    verdict: Literal["safe", "caution", "dangerous"]
    summary: str
    policy: Literal["allow", "ask", "block"]
    policy_reason: str
    findings: list[SkillHubScanFinding]
    severity_counts: SkillHubScanSeverityCounts
    tier1: SkillHubTier1Report | None


# ── local skills ──────────────────────────────────────────────────────────────────────────────


class SkillListRow(ResponseModel):
    """``get_skills`` row: ``tools/skills_tool.py::_find_all_skills`` (``category`` is ``null``
    for a top-level skill) annotated with enabled state, usage count and provenance."""

    name: str
    description: str
    category: str | None
    enabled: bool
    usage: int
    provenance: Literal["hub", "bundled", "external", "agent"] = Field(
        description='"external": mounted from ``skills.external_dirs`` (externally authored, not learned).')


class SkillToggleResponse(OkResponse):
    """``toggle_skill``."""

    name: str
    enabled: bool


class SkillContentResponse(ResponseModel):
    """``get_skill_content`` — raw SKILL.md text and its absolute path."""

    name: str
    content: str
    path: str


class SkillWriteChange(ResponseModel):
    """``_change`` — the new frontmatter description, clipped (``_description_preview``)."""

    description: str


class SkillLintWarning(ResponseModel):
    """``tools/skill_manager_tool.py::_attach_lint_findings`` row (advisory)."""

    severity: str
    rule: str
    message: str


class SkillCreateResponse(ResponseModel):
    """``tools/skill_manager_tool.py::_create_skill`` success payload (failures become a 400).
    ``path`` is relative to the skills dir when it lies under it; ``category`` only when given;
    ``system_prompt_preview`` only when the description is truncated in the prompt;
    ``lint_warnings`` + ``lint_hint`` only when the linter found something."""

    success: bool
    message: str
    path: str
    skill_md: str
    change: SkillWriteChange = Field(alias="_change")
    category: str | None = None
    hint: str
    system_prompt_preview: str | None = None
    lint_warnings: list[SkillLintWarning] | None = None
    lint_hint: str | None = None


class SkillContentUpdateResponse(ResponseModel):
    """``tools/skill_manager_tool.py::_edit_skill`` success payload (failures become a 400/404)."""

    success: bool
    message: str
    path: str
    change: SkillWriteChange = Field(alias="_change")
    system_prompt_preview: str | None = None
