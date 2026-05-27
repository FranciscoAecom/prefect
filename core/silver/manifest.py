from dataclasses import dataclass, field
import json
from pathlib import Path


@dataclass(frozen=True)
class SilverDatasetOutput:
    path: Path
    role: str
    label: str = ""

    def __post_init__(self):
        object.__setattr__(self, "path", Path(self.path))

    def to_json(self):
        return {
            "path": str(self.path),
            "role": self.role,
            "label": self.label,
        }


@dataclass(frozen=True)
class SilverOutputManifest:
    primary_output: SilverDatasetOutput | None = None
    xml_files: list[Path] = field(default_factory=list)
    sld_files: list[Path] = field(default_factory=list)
    quality_reports: dict[str, str | None] = field(default_factory=dict)
    manifest_path: Path | None = None

    @property
    def primary_output_path(self):
        if self.primary_output is None:
            return None
        return self.primary_output.path

    @property
    def dataset_outputs(self):
        outputs = []
        if self.primary_output is not None:
            outputs.append(self.primary_output)
        return outputs

    def with_artifacts(self, xml_files=None, sld_files=None):
        return SilverOutputManifest(
            primary_output=self.primary_output,
            xml_files=[Path(path) for path in (xml_files or [])],
            sld_files=[Path(path) for path in (sld_files or [])],
            quality_reports=dict(self.quality_reports),
            manifest_path=self.manifest_path,
        )

    def with_quality_reports(self, quality_reports):
        return SilverOutputManifest(
            primary_output=self.primary_output,
            xml_files=list(self.xml_files),
            sld_files=list(self.sld_files),
            quality_reports=dict(quality_reports or {}),
            manifest_path=self.manifest_path,
        )

    def with_manifest_path(self, manifest_path):
        return SilverOutputManifest(
            primary_output=self.primary_output,
            xml_files=list(self.xml_files),
            sld_files=list(self.sld_files),
            quality_reports=dict(self.quality_reports),
            manifest_path=Path(manifest_path) if manifest_path else None,
        )

    def to_json(self):
        return {
            "primary_output": (
                self.primary_output.to_json() if self.primary_output else None
            ),
            "xml_files": [str(path) for path in self.xml_files],
            "sld_files": [str(path) for path in self.sld_files],
            "quality_reports": dict(self.quality_reports),
            "manifest_path": str(self.manifest_path) if self.manifest_path else None,
        }


def quality_reports_from_summary(summary):
    return {
        "attribute_duplicates": summary.attr_report,
        "geometric_duplicates": summary.geom_report,
        "ogc_invalid_geometries": summary.ogc_report,
    }


def manifest_path_for_base(theme_output_dir, base_name):
    return Path(theme_output_dir) / f"{base_name}_manifest.json"


def persist_silver_manifest(manifest, theme_output_dir, base_name, persist_dataset=True):
    if not persist_dataset:
        return manifest

    manifest_path = manifest_path_for_base(theme_output_dir, base_name)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    updated_manifest = manifest.with_manifest_path(manifest_path)
    with manifest_path.open("w", encoding="utf-8") as file:
        json.dump(updated_manifest.to_json(), file, ensure_ascii=False, indent=2)
        file.write("\n")
    return updated_manifest


__all__ = [
    "SilverDatasetOutput",
    "SilverOutputManifest",
    "manifest_path_for_base",
    "persist_silver_manifest",
    "quality_reports_from_summary",
]
