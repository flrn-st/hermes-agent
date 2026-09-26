"""Response contracts for ``hermes_cli/web_routers/analytics.py``.

The analytics rows are SQL aggregates over ``state.db``: a ``SUM`` over the nullable
``sessions`` counters is ``null`` when every summed cell is ``NULL`` (always so for the
empty-window ``totals``), while ``COALESCE``d costs and ``COUNT``s never are.
"""

from __future__ import annotations

from hermes_cli.web_responses.base import ResponseModel
from hermes_cli.web_responses.models import ModelsDevCapabilities


class RawConfigYamlResponse(ResponseModel):
    """``get_config_raw`` — ``yaml`` is ``""`` when the profile's ``config.yaml`` does not exist."""

    yaml: str
    path: str


class AnalyticsUsageDailyRow(ResponseModel):
    """``_get_usage_analytics`` ``daily`` row; ``day`` is ``YYYY-MM-DD`` (``null`` only for a
    corrupt ``started_at`` cell)."""

    day: str | None
    input_tokens: int | None
    output_tokens: int | None
    cache_read_tokens: int | None
    reasoning_tokens: int | None
    estimated_cost: float
    actual_cost: float
    sessions: int
    api_calls: int


class AnalyticsAuxTaskUsage(ResponseModel):
    """``web_server_profiles._merge_aux_into_by_model`` ``aux_tasks`` entry."""

    task: str
    input_tokens: int
    output_tokens: int
    estimated_cost: float
    api_calls: int


class AnalyticsUsageModelRow(ResponseModel):
    """``_get_usage_analytics`` ``by_model`` row after ``_merge_aux_into_by_model``; ``aux_tasks``
    only on rows that auxiliary usage folded into (or created, for aux-only models)."""

    model: str
    input_tokens: int | None
    output_tokens: int | None
    estimated_cost: float
    sessions: int
    api_calls: int
    aux_tasks: list[AnalyticsAuxTaskUsage] | None = None


class AnalyticsTaskSummaryRow(ResponseModel):
    """``web_server_profiles._aux_task_summary`` row — auxiliary usage per task across models."""

    task: str
    input_tokens: int
    output_tokens: int
    estimated_cost: float
    api_calls: int
    models: list[str]


class AnalyticsUsageTotals(ResponseModel):
    total_input: int | None
    total_output: int | None
    total_cache_read: int | None
    total_reasoning: int | None
    total_estimated_cost: float
    total_actual_cost: float
    total_sessions: int
    total_api_calls: int | None


class AnalyticsSkillsSummary(ResponseModel):
    total_skill_loads: int
    total_skill_edits: int
    total_skill_actions: int
    distinct_skills_used: int


class AnalyticsSkillRow(ResponseModel):
    """``agent/insights.py::InsightsEngine._compute_skill_breakdown`` row; ``last_used_at`` is the
    epoch of the latest call carrying a timestamp."""

    skill: str
    view_count: int
    manage_count: int
    total_count: int
    percentage: float
    last_used_at: float | None


class AnalyticsSkillsBreakdown(ResponseModel):
    """``agent/insights.py::InsightsEngine._compute_skill_breakdown``."""

    summary: AnalyticsSkillsSummary
    top_skills: list[AnalyticsSkillRow]


class AnalyticsToolRow(ResponseModel):
    """``agent/insights.py::InsightsEngine._compute_tool_breakdown`` row."""

    tool: str
    count: int
    percentage: float


class AnalyticsUsageResponse(ResponseModel):
    """``_get_usage_analytics``."""

    daily: list[AnalyticsUsageDailyRow]
    by_model: list[AnalyticsUsageModelRow]
    by_task: list[AnalyticsTaskSummaryRow]
    totals: AnalyticsUsageTotals
    period_days: int
    skills: AnalyticsSkillsBreakdown
    tools: list[AnalyticsToolRow]


class AnalyticsModelCard(ResponseModel):
    """``_get_models_analytics`` card: one per (model, billing provider), auxiliary-only models
    included. ``provider`` is ``""`` when unrecorded; ``last_used_at`` is an epoch."""

    model: str
    provider: str
    input_tokens: int | None
    output_tokens: int | None
    cache_read_tokens: int | None
    reasoning_tokens: int | None
    estimated_cost: float
    actual_cost: float
    sessions: int
    api_calls: int
    tool_calls: int | None
    last_used_at: float | None
    avg_tokens_per_session: float | None
    capabilities: ModelsDevCapabilities


class AnalyticsModelsTotals(ResponseModel):
    distinct_models: int
    total_input: int | None
    total_output: int | None
    total_cache_read: int | None
    total_reasoning: int | None
    total_estimated_cost: float
    total_actual_cost: float
    total_sessions: int
    total_api_calls: int | None


class AnalyticsModelsResponse(ResponseModel):
    """``_get_models_analytics``."""

    models: list[AnalyticsModelCard]
    totals: AnalyticsModelsTotals
    period_days: int
