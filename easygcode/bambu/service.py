"""Unified print preparation service for EasyGcode."""

from __future__ import annotations

from easygcode.core import generate_gcode
from easygcode.jobs import PreparedPrint, PrintJob

from .gcode_adapter import add_bambu_guardrails
from .package_3mf import package_gcode_3mf
from .profiles import get_profile
from .studio import build_cli_hint, export_ascii_stl
from .validator import validate_build


class PrintService:
    """Prepare print artifacts for direct or Bambu Studio workflows."""

    def prepare(self, job: PrintJob) -> PreparedPrint:
        if job.mode == "direct":
            return self._prepare_direct(job)
        if job.mode == "bambu_studio":
            return self._prepare_bambu_studio(job)
        raise ValueError(f"Unsupported print mode: {job.mode}")

    def _prepare_direct(self, job: PrintJob) -> PreparedPrint:
        profile = get_profile(job.printer_id)
        result = generate_gcode(job.design)
        warnings = validate_build(result, profile)
        adapted_gcode = add_bambu_guardrails(result, profile)
        content = package_gcode_3mf(result, adapted_gcode)
        return PreparedPrint(
            mode="direct",
            status="ready",
            filename="easygcode-direct.gcode.3mf",
            mime_type="model/3mf",
            content=content,
            encoding="base64",
            warnings=[
                "Experimental direct-print package: review G-code manually before upload or remote start.",
                *warnings,
            ],
            summary={
                "printer": profile.label,
                "point_count": result.point_count,
                "estimated_bounds": result.estimated_bounds,
            },
        )

    def _prepare_bambu_studio(self, job: PrintJob) -> PreparedPrint:
        stl = export_ascii_stl(job)
        filename = "easygcode-design.stl"
        cli_hint = build_cli_hint(filename, "easygcode-sliced.3mf")
        return PreparedPrint(
            mode="bambu_studio",
            status="needs_bambu_studio",
            filename=filename,
            mime_type="model/stl",
            content=stl,
            encoding="text",
            warnings=[
                "Open the STL in Bambu Studio to choose machine, process, filament, "
                "supports, AMS, and preview before printing."
            ],
            summary={
                "material": job.material,
                "nozzle_diameter": job.nozzle_diameter,
                "bed_type": job.bed_type,
                "cli_hint": cli_hint,
            },
        )
