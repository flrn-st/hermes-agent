"""Response contracts for ``hermes_cli/web_routers/files.py``.

The managed-files routes (``/api/files*``) emit ``snake_case``; the ``/api/fs/*`` routes mirror
the Electron ``hermes:fs:*`` IPC and emit ``camelCase``.
"""

from __future__ import annotations

from hermes_cli.web_responses.base import ResponseModel, binary_body

# File-body routes return a FileResponse on every path (errors raise HTTPException).
MANAGED_FILE_DOWNLOAD_RESPONSES = {200: binary_body(
    "The file bytes; ``Content-Type`` is the MIME type guessed from the name.", "application/octet-stream")}
MANAGED_FILE_STREAM_RESPONSES = {200: binary_body(
    "Range-aware inline audio/video bytes (streamable extensions only); ``Content-Type`` is the guessed "
    "MIME type, ``application/octet-stream`` when unknown.", "audio/*", "video/*", "application/octet-stream")}


class MediaDataUrlResponse(ResponseModel):
    """``get_media``: an allowlisted image under the media roots as a base64 ``data:`` URL;
    ``proxy_remote_media``: an image fetched from an allowlisted remote CDN, in the same shape."""

    data_url: str


class ChatImageUploadResponse(ResponseModel):
    """``upload_chat_image``: where the clipboard image landed under ``HERMES_HOME/images/``."""

    ok: bool
    path: str
    name: str
    bytes: int
    mime_type: str


class ManagedFileEntry(ResponseModel):
    """``hermes_cli/web_server_files.py::_managed_file_entry``; ``size``/``mime_type`` are null
    for directories. A dangling symlink is a placeholder: ``broken_link: true`` with ``size``,
    ``mtime`` and ``mime_type`` null."""

    name: str
    path: str
    is_directory: bool
    size: int | None
    mtime: float | None
    mime_type: str | None
    broken_link: bool | None = None


class _ManagedFilesMeta(ResponseModel):
    """``hermes_cli/web_server_files.py::_managed_response_meta``: ``root``/``locked_root`` are
    the same locked root, null when the browser may roam."""

    root: str | None
    locked_root: str | None
    can_change_path: bool


class ManagedFileListResponse(_ManagedFilesMeta):
    """``list_managed_files``; ``parent`` is null at the filesystem or locked root."""

    path: str
    parent: str | None
    entries: list[ManagedFileEntry]


class ManagedFileReadResponse(_ManagedFilesMeta):
    """``read_managed_file``."""

    name: str
    path: str
    size: int
    mime_type: str
    data_url: str


class ManagedFileWriteResponse(_ManagedFilesMeta):
    """``_managed_write_result`` (upload, upload-stream, mkdir)."""

    ok: bool
    entry: ManagedFileEntry
    path: str


class ManagedFileDeleteResponse(_ManagedFilesMeta):
    """``delete_managed_file``."""

    ok: bool
    path: str


class FsListEntry(ResponseModel):
    name: str
    path: str
    isDirectory: bool


class FsListResponse(ResponseModel):
    """``fs_list``. A read failure is a 200 with ``entries: []`` and ``error`` (an errno name
    such as ``ENOENT``, else the OS ``strerror`` or ``"read-error"``)."""

    entries: list[FsListEntry]
    error: str | None = None


class FsReadTextResponse(ResponseModel):
    """``fs_read_text``: a UTF-8 (``replace``) preview capped at 512 KiB."""

    binary: bool
    byteSize: int
    language: str
    mimeType: str
    path: str
    text: str
    truncated: bool


class FsWriteTextResponse(ResponseModel):
    """``fs_write_text``."""

    ok: bool
    path: str
    byteSize: int


class FsDataUrlResponse(ResponseModel):
    """``fs_read_data_url``."""

    dataUrl: str


class FsGitRootResponse(ResponseModel):
    """``fs_git_root``: the nearest ancestor holding ``.git``, else null."""

    root: str | None


class FsDefaultCwdResponse(ResponseModel):
    """``fs_default_cwd``; ``branch`` is ``""`` outside a git checkout or on a detached HEAD."""

    cwd: str
    branch: str
