"""Response contracts for ``hermes_cli/web_routers/models.py``."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from hermes_cli.web_responses.base import OpenModel, ResponseModel


class ModelsDevCapabilities(ResponseModel):
    """``agent/models_dev.py::ModelCapabilities``; ``{}`` when models.dev has no row."""

    supports_tools: bool | None = None
    supports_vision: bool | None = None
    supports_reasoning: bool | None = None
    context_window: int | None = None
    max_output_tokens: int | None = None
    model_family: str | None = None


class ModelInfoResponse(ResponseModel):
    """``get_model_info``."""

    model: str
    provider: str
    auto_context_length: int
    config_context_length: int
    effective_context_length: int
    capabilities: ModelsDevCapabilities


class ModelOptionPricing(ResponseModel):
    """``hermes_cli/inventory.py::_apply_pricing`` — formatted $/Mtok strings (``""`` unknown,
    ``"free"``); the sale fields are Nous Portal-only."""

    input: str
    output: str
    cache: str | None = None
    free: bool
    discount_percent: int | None = None
    was_input: str | None = None
    was_output: str | None = None


class ModelOptionCapabilities(ResponseModel):
    """``hermes_cli/inventory.py::_apply_capabilities``."""

    fast: bool
    ultrafast: bool | None = Field(None, description="Only ever ``true``; absent when not offered.")
    reasoning: bool
    can_disable_reasoning: bool | None = None


class ModelOptionLimit(ResponseModel):
    """``hermes_cli/inventory.py::_apply_limits``: ``account`` — the whole login is rate-limited until
    ``resets_at`` (ISO); ``models`` — only these models are, each until its ISO time."""

    scope: Literal["account", "models"]
    resets_at: str | None = None
    models: dict[str, str] | None = None


class ModelOptionUsageWindow(ResponseModel):
    """One subscription usage window (``agent/account_usage.py::AccountUsageWindow``): how much is
    spent and when it rolls over (ISO). ``model``-scoped windows cap one model family only."""

    label: str
    used_percent: float
    resets_at: str | None
    scope: Literal["account", "model"]


class ModelOptionUsageAccount(ResponseModel):
    """One account of a multi-entry credential pool (``hermes_cli/inventory.py::_pool_usage_accounts``).
    ``id`` is a stable non-secret identity; ``windows`` is empty while usage is unknown; ``resets_at``
    is when a limited account is whole again (null when unknown)."""

    id: str
    label: str
    windows: list[ModelOptionUsageWindow]
    state: Literal["ready", "limited", "unknown", "unavailable"]
    resets_at: str | None


class ModelOptionUsage(ResponseModel):
    """``hermes_cli/inventory.py::_apply_usage`` (cache only): single-account providers carry
    ``windows``, multi-entry credential pools ``accounts`` instead."""

    windows: list[ModelOptionUsageWindow] | None = None
    accounts: list[ModelOptionUsageAccount] | None = None


class ModelOptionProviderRow(OpenModel):
    """One ``hermes_cli/inventory.py::build_models_payload`` provider row (the union of every field
    the builder sets). Same row as the ``model.options`` JSON-RPC result
    (``tui_gateway/contracts/config_free_tier_control.py::ModelOptionProvider``)."""

    slug: str
    name: str
    models: list[str] = Field(default_factory=list)
    total_models: int | None = None
    is_current: bool | None = None
    is_user_defined: bool | None = None
    source: str | None = None
    aliases: list[str] | None = None
    api_url: str | None = None
    auth_type: str | None = None
    authenticated: bool | None = None
    key_env: str | None = None
    warning: str | None = None
    featured_models: list[str] | None = None
    capabilities: dict[str, ModelOptionCapabilities] | None = None
    pricing: dict[str, ModelOptionPricing] | None = None
    pricing_pending: bool | None = None
    free_tier: bool | None = None
    free_tier_pending: bool | None = None
    free_tier_row: bool | None = None
    unavailable_models: list[str] | None = None
    limit: ModelOptionLimit | None = None
    usage: ModelOptionUsage | None = None


class ModelOptionsResponse(ResponseModel):
    """``hermes_cli/inventory.py::build_model_options_payload`` — the REST twin of the
    ``model.options`` JSON-RPC result."""

    providers: list[ModelOptionProviderRow]
    model: str = ""
    provider: str = ""


class RecommendedDefaultModelResponse(ResponseModel):
    """``get_recommended_default_model``; ``free_tier`` is only a bool for Nous and ``model`` may
    be ``""``."""

    provider: str
    model: str
    free_tier: bool | None


class AuxiliaryEffectiveRoute(ResponseModel):
    """The route an inheriting plugin task resolves to right now (``_get_auxiliary_task_config``)."""

    provider: str
    model: str
    base_url: str


class AuxiliaryTaskAssignment(ResponseModel):
    """One slot's own stored assignment. Plugin-registered tasks follow the built-in slots and add
    ``label``/``hint``/``plugin`` and ``inherit_from`` (base slot key or null); an inheriting row also
    carries ``effective``."""

    task: str
    provider: str
    model: str
    base_url: str
    reasoning_effort: str | None
    local_endpoint: bool
    label: str | None = None
    hint: str | None = None
    plugin: str | None = None
    inherit_from: str | None = None
    effective: AuxiliaryEffectiveRoute | None = None


class MainModelAssignment(ResponseModel):
    provider: str
    model: str


class AuxiliaryModelsResponse(ResponseModel):
    """``get_auxiliary_models`` — one row per ``_AUX_TASK_SLOTS`` entry, then one per
    plugin-registered auxiliary task of the profile."""

    tasks: list[AuxiliaryTaskAssignment]
    main: MainModelAssignment


class MoaSlot(ResponseModel):
    """``hermes_cli/moa_config.py::_clean_slot``; ``enabled`` only on reference slots."""

    provider: str
    model: str
    reasoning_effort: str | None = None
    enabled: bool | None = None


class MoaPreset(ResponseModel):
    """``hermes_cli/moa_config.py::_normalize_preset``; a ``None`` number means "provider default"."""

    enabled: bool
    reference_models: list[MoaSlot]
    aggregator: MoaSlot
    reference_temperature: float | None
    aggregator_temperature: float | None
    reference_timeout: float | None
    degraded_reference_policy: Literal["loud", "silent"]
    fanout: str = Field(description='"user_turn", "per_iteration" or "every_n:<N>".')


class MoaConfigResponse(MoaPreset):
    """``hermes_cli/moa_config.py::normalize_moa_config`` — named presets plus the default preset's
    fields flattened on top for older callers."""

    default_preset: str
    active_preset: str
    presets: dict[str, MoaPreset]
    privacy_filter: Literal["", "display", "full"]


class MoaConfigSaveResponse(MoaConfigResponse):
    """``set_moa_models`` — ``{"ok": true}`` plus the normalized config that was saved."""

    ok: bool


class StaleAuxiliaryPin(ResponseModel):
    """``hermes_cli/web_server_config.py::_stale_aux_pins``."""

    task: str
    provider: str
    model: str


class ModelAssignmentResponse(ResponseModel):
    """``set_model_assignment``: the expensive-model confirmation prompt (``ok: false``,
    ``confirm_required``), a main-slot assignment, an auxiliary assignment or the auxiliary
    ``__reset__`` — the union of ``_apply_main_assignment_sync`` and ``_apply_aux_assignment_sync``."""

    ok: bool
    scope: Literal["main", "auxiliary"]
    provider: str | None = None
    model: str | None = None
    confirm_required: bool | None = None
    confirm_message: str | None = None
    base_url: str | None = None
    gateway_tools: list[str] | None = None
    stale_aux: list[StaleAuxiliaryPin] | None = None
    tasks: list[str] | None = None
    reasoning_effort: str | None = None
    reset: bool | None = None
