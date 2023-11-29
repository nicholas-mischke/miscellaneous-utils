import pytest

from pathlib import Path
import sys
import importlib.util

from misc_utils import selfie

def test_selfie():
    class TestClass:
        @selfie("arg2")
        def __init__(self, arg1, arg2, arg3):
            # self.arg1 and self.arg3 are set automatically
            # self.arg2 is ignored due to the decorator argument
            pass
    obj = TestClass(*(1, 2, 3))
    assert (obj.arg1, hasattr(obj, "arg2"), obj.arg3) == (1, False, 3)

    # @selfie, instead of @selfie()
    class TestClass:
        @selfie
        def __init__(self, a, b, c):
            ...
    obj = TestClass(*(1, 2, 3))
    assert (obj.a, obj.b, obj.c) == (1, 2, 3)


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

if __name__ == "__main__":
    from pathlib import Path
    from pprint import pprint

    path = Path(__file__).absolute()

    # pytest.main([str(path)])
    pytest.main([f"{str(path)}::test_selfie"])

    test_file = Path(__file__).absolute()

    test_class_or_function = None
    test_method = None

    # test_class_or_function = ''
    # test_method = ''

    test_path = test_file
    if test_class_or_function is not None:
        test_path = f"{test_path}::{test_class_or_function}"
    if test_method is not None:
        test_path = f"{test_path}::{test_method}"

    args = [
        test_path,
        "-s",
        "--verbose",
    ]

    pytest.main(args)
