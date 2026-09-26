"""Response contracts for ``hermes_cli/web_routers/shared_metrics.py`` (the shared-metrics consent offer)."""

from __future__ import annotations

from hermes_cli.web_responses.base import ResponseModel


class SharedMetricsConsentResponse(ResponseModel):
    """``shared_metrics._read_consent`` (GET, and PUT after saving): ``shared_metrics_consent.consent_state``
    of the profile's raw config plus ``managed``. ``send`` is never true without ``enabled``; ``reask`` is
    an "off" answer from before the current offer version, which reads as undecided."""

    enabled: bool
    send: bool
    decided: bool
    reask: bool
    managed: bool

