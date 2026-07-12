"""Safety checks shared by Bambu-oriented backends."""

from __future__ import annotations

from easygcode.core import BuildResult

from .profiles import BambuProfile


class ValidationIssue(ValueError):
    """Raised when a print cannot be prepared safely."""


def validate_build(result: BuildResult, profile: BambuProfile) -> list[str]:
    """Validate generated toolpath bounds against a printer profile."""

    bounds = result.estimated_bounds
    max_x, max_y, max_z = profile.build_volume
    warnings: list[str] = []

    if bounds["min_x"] < 0 or bounds["min_y"] < 0 or bounds["min_z"] < 0:
        raise ValidationIssue(
            "Toolpath contains negative coordinates; move the design inside the build volume."
        )
    if bounds["max_x"] > max_x or bounds["max_y"] > max_y or bounds["max_z"] > max_z:
        raise ValidationIssue(
            f"Toolpath exceeds {profile.label} build volume "
            f"({max_x:g} x {max_y:g} x {max_z:g} mm)."
        )
    if result.spec.feedrate > profile.max_print_speed:
        warnings.append(
            f"Print feedrate {result.spec.feedrate} mm/min is above the conservative "
            f"profile limit of {profile.max_print_speed} mm/min."
        )
    if "G28" not in result.gcode:
        warnings.append(
            "Generated G-code does not include homing; review start G-code before direct printing."
        )
    if "M104" not in result.gcode and "M109" not in result.gcode:
        warnings.append(
            "Generated G-code does not set nozzle temperature; configure temperature before printing."
        )

    return warnings
