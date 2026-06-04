from dataclasses import dataclass, field
from pathlib import Path

from core.publish.config import PublishOptions


@dataclass(frozen=True)
class DownloadRunOptions:
    source_root: str | None = None
    output_dir: str | Path | None = None
    extract_base: str | Path | None = None
    output_base: str | Path | None = None
    force: bool = False
    emit_download_event: bool = True
    process_after_download: bool = True
    publish_after_process: bool = False


@dataclass(frozen=True)
class DownloadFlowOptions:
    run: DownloadRunOptions = field(default_factory=DownloadRunOptions)
    publish: PublishOptions = field(default_factory=PublishOptions)
