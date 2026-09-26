"""Response contracts for ``hermes_cli/web_routers/local_models.py``."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from hermes_cli.web_responses.base import ResponseModel


class LocalModelLoadProgress(ResponseModel):
    """``hermes_cli/local_runtime/load_progress.py::get_loading_progress`` entry."""

    stage: str
    value: float = Field(description="Progress within ``stage``, 0..1.")
    percent: int = Field(description="Composite 0-100 across all load stages.")


class LocalModelPlacement(ResponseModel):
    """``_loaded_models`` facts: the preset decision (``window``/``spilled``) and the window the
    live server actually granted; each group only when known."""

    window: int | None = None
    window_label: str | None = None
    spilled: bool | None = None
    granted_window: int | None = None
    granted_window_label: str | None = None


class LocalModelStagedRow(ResponseModel):
    """``_staged_row``: one downloaded variant (a split model's whole size)."""

    id: str
    size_bytes: int
    size_label: str


class LocalModelsStatusResponse(ResponseModel):
    """``local_models_status``."""

    enabled: bool
    tag: str
    configured_tag: str
    update_available: bool
    runtime_installed: bool
    runtime_backend: str | None
    server_running: bool
    server_base_url: str | None
    active_model_id: str | None
    loaded_models: dict[str, Literal["loaded", "ready", "loading"]]
    loading: dict[str, LocalModelLoadProgress]
    placement: dict[str, LocalModelPlacement]
    models: list[LocalModelStagedRow]
    models_dir: str


class LocalModelsHardwareResponse(ResponseModel):
    """``local_models_hardware``; the ``gpu_*``/``vram_used_bytes`` readouts are NVIDIA-only (null
    elsewhere)."""

    uma: bool
    vram_total_bytes: int
    vram_usable_bytes: int
    ram_total_bytes: int
    ram_available_bytes: int
    vram_label: str
    gpu_name: str | None
    gpu_util_percent: int | None
    vram_used_bytes: int | None


class LocalModelCatalogRow(ResponseModel):
    """``_catalog_row``. ``fits=false`` rows price the smallest build and add ``fit_detail``;
    ``fits=true`` rows add the selected variant, plus the start window unless physics refused."""

    id: str
    display_name: str
    description: str
    native_context: int
    native_context_label: str
    recommended: bool
    recommended_reason: str | None
    downloaded: bool
    downloaded_model_id: str | None
    downloaded_quant: str | None
    mtp: bool
    vision: bool
    needs_engine: bool
    min_engine: str | None
    fits: bool
    size_bytes: int
    size_label: str
    fit_summary: str
    fit_detail: str | None = None
    model_id: str | None = None
    quant: str | None = None
    quant_validated: bool | None = None
    variant_count: int | None = None
    quant_reason: str | None = None
    start_window: int | None = None
    start_window_label: str | None = None
    spilled: bool | None = None


class LocalModelsCatalogResponse(ResponseModel):
    """``local_models_catalog``."""

    models: list[LocalModelCatalogRow]


class LocalModelsRuntimeInstallResponse(ResponseModel):
    """``local_models_runtime_install``."""

    job_id: str
    backend: str
    tag: str


class LocalModelsDownloadResponse(ResponseModel):
    """``local_models_download`` / ``local_models_download_browsed``: ``job_id`` is null (and
    ``already_downloaded`` true) when every file is already on disk."""

    job_id: str | None
    model_id: str
    already_downloaded: bool | None = None


class LocalModelsDownloadPauseResponse(ResponseModel):
    """``local_models_download_pause``; ``paused`` false when the job is not pausable now."""

    ok: bool
    paused: bool


class LocalModelsDownloadResumeResponse(ResponseModel):
    """``local_models_download_resume``."""

    ok: bool
    resumed: bool


class LocalModelsQuickstartResponse(ResponseModel):
    """``local_models_quickstart``; ``model_id`` is the catalog family id."""

    job_id: str
    model_id: str
    display_name: str
    needs_runtime: bool
    needs_download: bool
    download_bytes: int


class LocalModelsServerResponse(ResponseModel):
    """``local_models_server``."""

    ok: bool
    action: Literal["stop", "start"]


class LocalModelsActivateResponse(ResponseModel):
    """``local_models_activate``."""

    job_id: str


class LocalModelJob(ResponseModel):
    """``_job`` record as rendered by ``_job_view``."""

    job_id: str
    kind: Literal["runtime-install", "model-download", "quickstart", "model-activate"]
    target: str
    model_id: str | None = Field(description="Catalog/variant id for download-type jobs.")
    status: Literal["running", "paused", "done", "error"]
    phase: str = Field(description="Current step name (``starting``, ``downloading``, ``done``, ...).")
    detail: str
    total_bytes: int | None
    done_bytes: int
    started_at: float
    error: str | None
    ranges: dict[str, list[list[int]]] = Field(
        default_factory=dict, description="Per-destination half-open ``[start, end)`` byte runs (``pm/downloader.py``).")
    bytes_per_sec: float | None = Field(None, description="Only while running and measurable.")
    eta_seconds: int | None = Field(None, description="With ``bytes_per_sec``; null when the total is unknown.")
    pause_requested: bool
    can_pause: bool
    can_resume: bool
    percent: int | None = Field(None, description="Only once ``total_bytes`` is known.")


class LocalModelsJobsResponse(ResponseModel):
    """``local_models_jobs``: running/paused first, then up to 20 settled jobs."""

    jobs: list[LocalModelJob]


class LocalModelSearchHit(ResponseModel):
    """``hermes_cli/local_runtime/hf_browse.py::HFModelHit``."""

    repo: str
    downloads: int
    likes: int
    updated: str
    gated: bool


class LocalModelsSearchResponse(ResponseModel):
    """``local_models_search``."""

    hits: list[LocalModelSearchHit]


class LocalModelRepoFile(ResponseModel):
    """``hermes_cli/local_runtime/hf_browse.py::HFFileGroup`` priced by ``rough_fit``."""

    label: str
    paths: list[str] = Field(description="Repo-relative; every part of a split GGUF, in order.")
    total_bytes: int
    fit: Literal["fits-gpu", "needs-ram", "too-big", "unknown"]


class LocalModelsSearchFilesResponse(ResponseModel):
    """``local_models_search_files``."""

    files: list[LocalModelRepoFile]


class LocalModelsSideloadResponse(ResponseModel):
    """``local_models_sideload``."""

    ok: bool
    model_id: str
    already_present: bool | None = None
