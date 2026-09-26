"""Response contracts for ``hermes_cli/web_routers/config_env.py``."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from hermes_cli.web_responses.base import OpenModel, ResponseModel


class ConfigResponse(OpenModel):
    """``get_config`` — the user's config tree through ``_normalize_config_for_web`` minus the
    ``_``-prefixed internal keys. The sections are owned by ``DEFAULT_CONFIG`` / config.yaml, so
    only the keys the normaliser itself rewrites are typed."""

    # Flattened from a dict-form ``model`` (its ``default``/``name``); absent only when
    # ``include_defaults=false`` and the file has no ``model``.
    model: str | None = None
    # Virtual field (``model.context_length``; 0 = auto-detect).
    model_context_length: int


class ConfigDefaultsResponse(OpenModel):
    """``get_defaults`` — ``hermes_cli.config.DEFAULT_CONFIG`` verbatim (including
    ``_config_version``); its tree is owned by ``hermes_cli/config_defaults.py``."""


class ConfigSchemaField(ResponseModel):
    """One ``hermes_cli/web_server_config.py::_build_schema_from_config`` entry, with any
    ``_SCHEMA_OVERRIDES`` layered on (``_select`` adds ``options``/``searchable``/``clearable``).
    Dict values recurse into dotted keys, so ``_infer_type``'s ``"object"`` never reaches the wire."""

    type: Literal["boolean", "number", "list", "string", "select"]
    description: str
    category: str
    options: list[str] | None = None
    searchable: bool | None = None
    clearable: bool | None = None


class ConfigSchemaResponse(ResponseModel):
    """``get_schema`` — ``_schema_with_dynamic_provider_options`` keyed by dotted config path."""

    fields: dict[str, ConfigSchemaField]
    category_order: list[str]


class EgressStatusResponse(ResponseModel):
    """``get_egress_status`` — ``hermes_cli/proxy_cli.py::format_status_text``."""

    text: str


class EnvProviderProfile(ResponseModel):
    """``_catalog_provider_env_metadata._profile``: one provider sharing an env var with others."""

    provider: str
    provider_label: str
    description: str
    url: str | None
    primary: bool


class EnvVarInfo(ResponseModel):
    """One ``_get_env_vars_sync._row``: ``OPTIONAL_ENV_VARS`` prose layered over the provider
    catalog's card metadata. ``GET /api/env`` returns ``{VAR_NAME: EnvVarInfo}``."""

    is_set: bool
    redacted_value: str | None
    description: str
    url: str | None
    category: str
    is_password: bool
    tools: list[str]
    advanced: bool
    channel_managed: bool
    provider: str
    provider_label: str
    provider_profiles: list[EnvProviderProfile] = Field(
        description="Every built-in provider this credential serves; [] when only one does.")
    provider_primary: bool
    custom: bool


class EnvVarSaveResponse(ResponseModel):
    """``set_env_var`` — ``hermes_cli/credential_lifecycle.py::save_provider_env_credential``."""

    ok: bool
    key: str
    config_updates: list[str]


class EnvVarRemoveResponse(ResponseModel):
    """``remove_env_var`` — ``credential_lifecycle.py::remove_provider_env_credential`` (the
    handler 404s when ``found`` is false, so a 200 always carries ``found: true``)."""

    ok: bool
    key: str
    removed: bool
    pool_pruned: list[str]
    providers: list[str]
    config_scrubbed: list[str]
    found: bool


class EnvVarRevealResponse(ResponseModel):
    """``reveal_env_var``."""

    key: str
    value: str


class CustomEndpointRow(ResponseModel):
    """One ``_endpoint_row``."""

    id: str
    name: str
    base_url: str
    model: str
    models: list[str]
    api_mode: Literal["", "chat_completions", "codex_responses", "anthropic_messages"]
    # Raw ``context_length`` from the providers/custom_providers entry (the dashboard writes an int).
    context_length: int | None
    discover_models: bool
    has_api_key: bool
    # ``«redacted:…»`` for a plaintext key, ``${KEY_ENV}`` for a key_env reference.
    api_key_preview: str | None
    is_current: bool
    source: Literal["providers", "custom_providers", "direct-config"]


class CustomEndpointCurrentModel(ResponseModel):
    provider: str
    model: str
    base_url: str


class CustomEndpointListResponse(ResponseModel):
    """``list_custom_endpoints`` — ``_custom_endpoint_response``."""

    endpoints: list[CustomEndpointRow]
    current: CustomEndpointCurrentModel


class CustomEndpointUpsertResponse(CustomEndpointListResponse):
    """``upsert_custom_endpoint`` — the refreshed list plus the saved endpoint's id."""

    ok: bool
    id: str


class CustomEndpointDeleteResponse(CustomEndpointListResponse):
    """``delete_custom_endpoint`` — the refreshed list."""

    ok: bool


class CustomEndpointActivateResponse(ResponseModel):
    """``activate_custom_endpoint``."""

    ok: bool
    provider: str
    model: str


class ProviderModelEntry(ResponseModel):
    """One ``hermes_cli/web_server_profiles.py::_parse_model_entries`` row; the alias metadata is
    only present when the endpoint advertised it."""

    id: str
    canonical_model: str | None = None
    reasoning_effort: str | None = None


class CustomEndpointValidateResponse(ResponseModel):
    """``validate_custom_endpoint`` — the early failures carry only the first four keys."""

    ok: bool
    reachable: bool
    message: str
    models: list[str]
    model_details: list[ProviderModelEntry] | None = None
    # Canonicalised ``api_mode`` (unknown spellings pass through) or the URL auto-detect.
    transport_checked: str | None = None
    resolved_base_url: str | None = None


class ProviderCredentialValidateResponse(ResponseModel):
    """``validate_provider_credential``; ``models``/``model_details``/``resolved_base_url`` only on
    the ``OPENAI_BASE_URL`` connectivity branch."""

    ok: bool
    reachable: bool
    message: str
    models: list[str] | None = None
    model_details: list[ProviderModelEntry] | None = None
    resolved_base_url: str | None = None
