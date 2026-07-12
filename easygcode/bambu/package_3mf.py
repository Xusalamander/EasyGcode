"""Create downloadable Bambu-style G-code 3MF packages.

This packages the generated G-code in a zip container with metadata so users can
inspect/download the artifact. It is intentionally conservative and does not
pretend to be a stable vendor API for remote print submission.
"""

from __future__ import annotations

import base64
import json
from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile

from easygcode.core import BuildResult


def package_gcode_3mf(result: BuildResult, adapted_gcode: str) -> str:
    """Return a base64-encoded `.gcode.3mf` zip payload."""

    metadata = {
        "generator": "EasyGcode",
        "mode": "direct",
        "template": result.spec.template,
        "point_count": result.point_count,
        "estimated_bounds": result.estimated_bounds,
    }
    buffer = BytesIO()
    with ZipFile(buffer, "w", ZIP_DEFLATED) as archive:
        archive.writestr("Metadata/easygcode.json", json.dumps(metadata, indent=2))
        archive.writestr("plate_1.gcode", adapted_gcode)
    return base64.b64encode(buffer.getvalue()).decode("ascii")
