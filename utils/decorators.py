import inspect
import functools
from typing import Any, Callable
import sys

from utils.params import ParamProbe


def selfie(*ignore_parameters: str) -> Callable:
    """
    Automatically assign the parameters of a method (likely __init__) to
    instance variables, ignoring any specified parameters.

    Args:
    ----
        *ignore_parameters (str): Names of the parameters to be ignored.

    Returns:
    -------
        Callable: A decorator function.

    Example:
    -------
    class MyClass:

        @selfie('arg2')
        def __init__(self, arg1, arg2, arg3):
            # self.arg1 and self.arg3 are set automatically
            # self.arg2 is ignored due to the decorator argument
            ...
    """

    def decorator(func: Callable) -> Callable:
        parameters = ParamProbe(func, remove_self=True).names

        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            # Combine positional and keyword arguments
            all_args = {**dict(zip(parameters, args, strict=True)), **kwargs}

            # Assign instance variables
            for name, value in all_args.items():
                if name not in ignore_parameters:
                    setattr(self, name, value)

            return func(self, *args, **kwargs)

        return wrapper

    return decorator


def export(defn: Any) -> Any:
    """
    Export a definition to the top of its module.

    In Python, the `__all__` attribute in a module specifies which symbols are exported
    when `from module import *` is used. By default, if `__all__` isn't defined,
    all symbols without a leading underscore are exported. This function adds
    the provided definition to the module's `__all__` attribute, thus making it
    part of the module's public API when using the `from module import *` statement.

    Args:
    ----
        defn (Any): The definition (class, function, etc.) to be exported.

    Returns:
    -------
        Any: The same definition that was passed in.

    References:
    ----------
        https://www.youtube.com/watch?v=0oTh1CXRaQ0 (timestamp: 34:07)
        Thanks David Beazley!
    """
    module_name = defn.__module__

    # Attempt to get the module from sys.modules, if not fallback to inspect
    module = sys.modules.get(module_name, inspect.getmodule(defn))

    if module is None:
        raise ImportError(f"Module {module_name} could not be found.")

    # Ensure __all__ exists in the module
    if "__all__" not in module.__dict__:
        setattr(module, "__all__", [])

    module.__all__.append(defn.__name__)
    return defn


def apply_decorators(func, *decorators):
    """
    Apply any number of decorators to a function
    """
    for decorator in reversed(decorators):
        func = decorator(func)
    return func
