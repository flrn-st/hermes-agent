"""Response contracts for ``hermes_cli/web_routers/memory_providers.py``."""

from __future__ import annotations

from typing import Literal

from hermes_cli.web_responses.base import JsonValue, OkResponse, ResponseModel


class MemoryProviderExternalDependency(ResponseModel):
    """``hermes_cli/web_server_memory.py::_memory_provider_setup_manifest`` — blank strings when the
    manifest omits a key."""

    name: str
    install: str
    check: str


class MemoryProviderSetupInfo(ResponseModel):
    """``hermes_cli/web_server_memory.py::_memory_provider_setup_info``."""

    pip_dependencies: list[str]
    python_dependencies_declared: bool
    external_dependencies: list[MemoryProviderExternalDependency]
    required_env: list[str]
    dependencies_installed: bool


class MemoryProviderStatusRow(ResponseModel):
    """One ``hermes_cli/web_server_memory.py::_discover_memory_provider_statuses`` row."""

    name: str
    description: str
    available: bool
    configured: bool
    status: Literal["missing", "unavailable", "needs_config", "ready"]
    setup: MemoryProviderSetupInfo


class MemoryProviderFieldOption(ResponseModel):
    value: str
    label: str
    description: str


class MemoryProviderDeclaredField(ResponseModel):
    """One field of ``_declared_provider_payload`` (``plugins/memory/config_schema.py::ProviderField``).
    ``value`` is always the string the generic panel edits; secrets are ``""`` (write-only)."""

    key: str
    label: str
    kind: str
    description: str
    info: str
    placeholder: str
    inline: bool
    group: str
    options: list[MemoryProviderFieldOption]
    value: str
    is_set: bool


class MemoryProviderDeclaredConfigResponse(ResponseModel):
    """``get_memory_provider_config`` with ``surface=declared`` (``_declared_provider_payload``, or an
    empty panel when the provider declares no ``config_schema.py``)."""

    name: str
    label: str
    docs_url: str
    fields: list[MemoryProviderDeclaredField]


class MemoryProviderLegacyField(ResponseModel):
    """One field of ``_memory_provider_payload`` (normalised by
    ``hermes_cli/web_server_memory.py::_normalize_memory_provider_schema``). ``value`` is a bool for
    ``boolean`` fields and a string otherwise (``""`` for secrets); the bounds pass through from the
    provider's ``get_config_schema()`` unchanged."""

    key: str
    label: str
    kind: Literal["secret", "select", "boolean", "integer", "number", "text"]
    description: str
    placeholder: str
    required: bool
    value: str | bool
    is_set: bool
    options: list[MemoryProviderFieldOption]
    url: str
    when: dict[str, JsonValue] | None
    minimum: JsonValue
    maximum: JsonValue
    step: JsonValue


class MemoryProviderLegacyConfigResponse(ResponseModel):
    """``get_memory_provider_config`` without ``surface=declared`` (``_memory_provider_payload``, or
    an empty field list when the provider cannot be loaded)."""

    name: str
    label: str
    fields: list[MemoryProviderLegacyField]
    setup: MemoryProviderSetupInfo


class MemoryProviderSetupStepResult(ResponseModel):
    """``_command_result``; ``returncode`` is ``None`` when no process ran."""

    kind: Literal["pip", "setup", "external_check", "external_install"]
    name: str
    status: str
    command: str
    returncode: int | None
    stdout: str
    stderr: str


class MemoryProviderSetupResponse(ResponseModel):
    """``setup_memory_provider`` → ``_install_memory_provider_setup``; ``status`` is ``None`` when
    discovery no longer lists the provider."""

    ok: bool
    provider: str
    results: list[MemoryProviderSetupStepResult]
    status: MemoryProviderStatusRow | None


class MemoryProviderConfigSaveResponse(OkResponse):
    """``update_memory_provider_config``; ``active`` only on the legacy surface, which also
    activates the provider."""

    active: str | None = None
