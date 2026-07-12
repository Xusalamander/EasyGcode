import py_compile
from pathlib import Path

from easygcode.app import EasyGcodeRequestHandler, main


def test_app_module_compiles():
    app_path = Path(__file__).parents[1] / "easygcode" / "app.py"
    py_compile.compile(str(app_path), doraise=True)


def test_app_exports_handler_and_entrypoint():
    assert EasyGcodeRequestHandler.__name__ == "EasyGcodeRequestHandler"
    assert callable(main)
