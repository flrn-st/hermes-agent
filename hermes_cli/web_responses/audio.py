"""Response contracts for ``hermes_cli/web_routers/audio.py`` (HTTP routes; the speak-stream
WebSocket is not part of the OpenAPI document)."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from hermes_cli.web_responses.base import JsonValue, OkResponse, OpenModel, ResponseModel


class AudioTranscriptionResponse(OkResponse):
    """``transcribe_audio_upload``; ``transcript`` is ``""`` when no speech was detected."""

    transcript: str
    provider: str | None


class SttHallucinationFilter(ResponseModel):
    """``tools/voice_client_config.py::stt_hallucination_filter``: the Whisper-silence filter the
    relay path applies, so a client-direct transcription agrees with a relayed one."""

    phrases: list[str]
    repeat_regex: str  # a JS regex source


class VoiceClientSttConfig(ResponseModel):
    """``tools/voice_client_config.py::_resolve_stt_client_config``. ``mode: "relay"`` carries only
    ``reason``; ``"direct"`` carries the provider wire, credentials and ``hallucination_filter``.
    ``streaming`` (live dictation over ``/api/audio/transcribe-stream``) is stamped on either
    verdict by ``resolve_client_voice_config``; absent when that probe fails or on the route's own
    fallback."""

    mode: Literal["relay", "direct"]
    reason: str | None = None
    wire: Literal["openai-multipart", "xai-stt", "elevenlabs-stt"] | None = None
    provider: str | None = None
    base_url: str | None = None
    api_key: str | None = None
    model: str | None = None
    language: str | None = None
    timeout_s: float | None = None
    hallucination_filter: SttHallucinationFilter | None = None
    streaming: bool | None = None


class VoiceClientTtsConfig(ResponseModel):
    """``tools/voice_client_config.py::_resolve_tts_client_config`` (same relay/direct split as
    STT). ``speed`` is ``null`` for providers that take none; ``extra_body`` is OpenAI-only."""

    mode: Literal["relay", "direct"]
    reason: str | None = None
    wire: Literal["openai-speech", "elevenlabs-tts"] | None = None
    provider: str | None = None
    base_url: str | None = None
    api_key: str | None = None
    model: str | None = None
    voice: str | None = None
    speed: float | None = None
    extra_body: dict[str, JsonValue] | None = Field(
        default=None, description="Optional ``lang_code`` / ``consent_attestation`` from ``tts.openai``.")
    min_len: int | None = None


class VoiceClientConfigResponse(OkResponse):
    """``get_client_voice_config`` — ``tools/voice_client_config.py::resolve_client_voice_config``."""

    stt: VoiceClientSttConfig
    tts: VoiceClientTtsConfig


class VoiceLiveStatusResponse(OkResponse):
    """``get_voice_live_status`` — ``tools/voice_live.py::resolve_gpt_live_status``."""

    mode: Literal["chained", "gpt-live"]
    available: bool
    reason: str | None
    model: str
    voice: str


class VoiceLiveSessionInfo(OpenModel):
    id: str | None = None


class VoiceLiveTransport(OpenModel):
    type: str | None = None
    sdp: str | None = None


class VoiceLiveSessionResponse(OpenModel):
    """``create_voice_live_session`` — ``{"ok": true}`` merged over the vendor's
    ``POST /v1/live/sessions`` response (``tools/voice_live.py::create_webrtc_session``), which the
    vendor owns; the session id and SDP answer are the fields the renderer reads."""

    ok: bool
    session: VoiceLiveSessionInfo | None = None
    transport: VoiceLiveTransport | None = None


class ElevenLabsVoice(ResponseModel):
    voice_id: str
    name: str
    label: str


class ElevenLabsVoicesResponse(ResponseModel):
    """``get_elevenlabs_voices``; ``available: false`` with no key configured, or with
    ``error: "unauthorized"`` when ElevenLabs rejected the key."""

    available: bool
    voices: list[ElevenLabsVoice]
    error: Literal["unauthorized"] | None = None


class AudioSpeakResponse(OkResponse):
    """``speak_text``."""

    data_url: str = Field(description="``data:<mime_type>;base64,<audio>``.")
    mime_type: Literal["audio/mpeg", "audio/ogg", "audio/wav", "audio/flac"]
    provider: str | None


class TtsLeaseResponse(OkResponse):
    """``tts_lease`` — the request's ``lease`` / ``active`` plus
    ``tools/tts_tool_lifecycle.py::acquire_tts_lease`` (warm-up result) or ``release_tts_lease``
    (``released``). A lifecycle exception is reported in the body (``action: "error"``,
    ``leases: null``), never as an HTTP error."""

    lease: str
    active: bool
    leases: int | None
    provider: str | None = None
    warmed: bool | None = None
    action: Literal["noop", "loaded", "cached", "warmed", "installed", "error"] | None = None
    error: str | None = None
    elapsed_ms: int | None = None
    released: int | None = None


class SttLeaseResponse(OkResponse):
    """``stt_lease`` — the request's ``lease`` / ``active`` plus ``tools/stt_lease.py::acquire_stt_lease``
    (``warm_stt_provider``'s warm-up result and the holder count) or ``release_stt_lease`` (the count
    only). A lease exception is reported in the body (``action: "error"``, ``leases: null``), never as
    an HTTP error."""

    lease: str
    active: bool
    leases: int | None
    provider: str | None = None
    warmed: bool | None = None
    action: Literal["noop", "loaded", "cached", "error"] | None = None
    error: str | None = None
    elapsed_ms: int | None = None