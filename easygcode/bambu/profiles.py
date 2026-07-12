"""Small built-in Bambu printer profile catalogue.

The values are conservative defaults for local validation. They are not a
replacement for the printer/vendor profile used by Bambu Studio.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class BambuProfile(BaseModel):
    """Printer constraints used by validation and UI summaries."""

    id: str
    label: str
    build_volume: tuple[float, float, float]
    max_print_speed: int = Field(..., description="Conservative speed limit in mm/min")
    max_nozzle_temperature: int = 300
    max_bed_temperature: int = 120


_PROFILES: dict[str, BambuProfile] = {
    "generic": BambuProfile(
        id="generic",
        label="Generic Bambu-compatible printer",
        build_volume=(256, 256, 256),
        max_print_speed=12000,
    ),
    "bambu_x1c": BambuProfile(
        id="bambu_x1c",
        label="Bambu Lab X1 Carbon",
        build_volume=(256, 256, 256),
        max_print_speed=12000,
    ),
    "bambu_p1s": BambuProfile(
        id="bambu_p1s",
        label="Bambu Lab P1S",
        build_volume=(256, 256, 256),
        max_print_speed=12000,
    ),
    "bambu_a1": BambuProfile(
        id="bambu_a1",
        label="Bambu Lab A1",
        build_volume=(256, 256, 256),
        max_print_speed=10000,
    ),
}


def list_profiles() -> list[BambuProfile]:
    """Return available built-in printer profiles."""

    return list(_PROFILES.values())


def get_profile(profile_id: str) -> BambuProfile:
    """Return a profile by id, falling back to the generic profile."""

    return _PROFILES.get(profile_id, _PROFILES["generic"])
