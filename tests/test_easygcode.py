from easygcode import DesignSpec, generate_gcode, list_templates


def test_templates_are_user_facing():
    templates = list_templates()
    assert {template.id for template in templates} == {"line", "rectangle", "grid", "spiral"}
    assert all(template.label for template in templates)


def test_generate_gcode_uses_fullcontrol_core():
    result = generate_gcode(DesignSpec(template="rectangle", width=10, depth=5, spacing=2))
    assert result.point_count == 5
    assert "GCode created with FullControl" in result.gcode
    assert "X10" in result.gcode
    assert result.estimated_bounds == {
        "min_x": 0,
        "max_x": 10,
        "min_y": 0,
        "max_y": 5,
        "min_z": 0.2,
        "max_z": 0.2,
    }
