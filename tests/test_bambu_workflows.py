import base64
import zipfile
from io import BytesIO

from easygcode import DesignSpec, PrintJob
from easygcode.bambu import PrintService, list_profiles
from easygcode.bambu.studio import build_cli_hint


def test_printer_profiles_are_available():
    profiles = list_profiles()
    assert {profile.id for profile in profiles} >= {
        "generic",
        "bambu_x1c",
        "bambu_p1s",
        "bambu_a1",
    }


def test_direct_backend_packages_gcode_3mf():
    job = PrintJob(
        mode="direct",
        printer_id="bambu_p1s",
        design=DesignSpec(template="line", width=5, depth=5, spacing=1),
    )

    prepared = PrintService().prepare(job)

    assert prepared.status == "ready"
    assert prepared.filename.endswith(".gcode.3mf")
    package = base64.b64decode(prepared.content)
    with zipfile.ZipFile(BytesIO(package)) as archive:
        assert "Metadata/easygcode.json" in archive.namelist()
        assert "plate_1.gcode" in archive.namelist()
        assert "EasyGcode direct Bambu package" in archive.read("plate_1.gcode").decode()


def test_bambu_studio_backend_exports_stl_and_cli_hint():
    job = PrintJob(
        mode="bambu_studio",
        design=DesignSpec(template="rectangle", width=10, depth=5),
    )

    prepared = PrintService().prepare(job)

    assert prepared.status == "needs_bambu_studio"
    assert prepared.filename.endswith(".stl")
    assert prepared.content.startswith("solid easygcode")
    assert "--export-3mf" in prepared.summary["cli_hint"]


def test_cli_hint_is_reviewable_command():
    hint = build_cli_hint("design.stl", "output.3mf")
    assert "design.stl" in hint
    assert "output.3mf" in hint
