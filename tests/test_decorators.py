# trunk-ignore(ruff/F401)
import pytest

from pathlib import Path
import sys
import importlib.util

from utils.decorators import selfie, export


def test_selfie():
    class TestClass:
        @selfie("arg2")
        def __init__(self, arg1, arg2, arg3):
            # self.arg1 and self.arg3 are set automatically
            # self.arg2 is ignored due to the decorator argument
            pass

    obj = TestClass(*(1, 2, 3))

    assert (obj.arg1, hasattr(obj, "arg2"), obj.arg3) == (1, False, 3)


@pytest.mark.parametrize(
    "module_name, contains", [("not_in__all__.py", False), ("in__all__.py", True)]
)
def test_export(module_name: str, contains: bool):
    module_path = Path(__file__).parent / "test_misc_module" / module_name

    spec = importlib.util.spec_from_file_location(module_path.stem, module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module.__name__] = module  # Add the module to sys.modules
    spec.loader.exec_module(module)

    # Check the presence/absence of MyClass in the __all__ attribute based on the contains parameter
    assert ("MyClass" in getattr(module, "__all__", [])) == contains
