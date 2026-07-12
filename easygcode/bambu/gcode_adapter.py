"""Bambu-oriented G-code adaptation helpers."""

from __future__ import annotations

from easygcode.core import BuildResult

from .profiles import BambuProfile


def add_bambu_guardrails(result: BuildResult, profile: BambuProfile) -> str:
    """Wrap FullControl G-code with conservative comments and lifecycle commands.

    The wrapper deliberately stays minimal. Full Bambu-specific start sequences
    should remain profile-driven and user-reviewable before direct printing.
    """

    header = [
        "; EasyGcode direct Bambu package",
        f"; Printer profile: {profile.label}",
        f"; Bounds: {result.estimated_bounds}",
        "G90 ; absolute positioning",
        "M83 ; relative extrusion",
    ]
    footer = [
        "M400 ; wait for moves to finish",
        "M104 S0 ; turn off hotend",
        "M140 S0 ; turn off bed",
        "M107 ; turn off fan",
        "; End EasyGcode direct package",
    ]
    return "\n".join([*header, result.gcode, *footer])
