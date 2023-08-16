
from typing import Any, Callable, Dict, Tuple, Union
import inspect

EMPTY = inspect.Parameter.empty

POSITIONAL_ONLY = inspect.Parameter.POSITIONAL_ONLY
POSITIONAL_OR_KEYWORD = inspect.Parameter.POSITIONAL_OR_KEYWORD
VAR_POSITIONAL = inspect.Parameter.VAR_POSITIONAL
KEYWORD_ONLY = inspect.Parameter.KEYWORD_ONLY
VAR_KEYWORD = inspect.Parameter.VAR_KEYWORD


class Param:
    def __init__(self, inspect_param: inspect.Parameter):
        self.name = inspect_param.name
        self.kind = str(inspect_param.kind).split(".")[-1]
        self.default = inspect_param.default
        self.annotation = inspect_param.annotation

    # ... Argument kind ...
    @property
    def can_pass_pos_arg(self) -> bool:
        """Check if the parameter can be passed as a positional argument."""
        return self.is_pos_only or self.is_pos_or_kw or self.is_var_pos

    @property
    def can_pass_kw_arg(self) -> bool:
        """Check if the parameter can be passed as a keyword argument."""
        return self.is_pos_or_kw or self.is_kw_only or self.is_var_kw

    # ... Param kind ...
    @property
    def is_pos_only(self) -> bool:
        """Check if the parameter is positional only."""
        return self.kind == "POSITIONAL_ONLY"

    @property
    def is_pos_or_kw(self) -> bool:
        """Check if the parameter is positional or keyword."""
        return self.kind == "POSITIONAL_OR_KEYWORD"

    @property
    def is_var_pos(self) -> bool:
        """Check if the parameter is variable positional."""
        return self.kind == "VAR_POSITIONAL"

    @property
    def is_kw_only(self) -> bool:
        """Check if the parameter is keyword only."""
        return self.kind == "KEYWORD_ONLY"

    @property
    def is_var_kw(self) -> bool:
        """Check if the parameter is variable keyword."""
        return self.kind == "VAR_KEYWORD"

    # ... Default ...
    @property
    def is_optional(self) -> bool:
        """Check if the parameter has a default value."""
        return self.default is not EMPTY

    def __str__(self):
        return (
            'Param('
            f'name="{self.name}", '
            f'default=\"{"EMPTY" if self.default is EMPTY else self.default}\", '
            f'kind="{self.kind}", '
            f'annotation=\"{"EMPTY" if self.annotation is EMPTY else self.annotation}\"'
            ')'
        )

    def __eq__(self, other):
        return (
            self.name == other.name
            and self.kind == other.kind
            and self.default == other.default
            and self.annotation == other.annotation
        )


class ParamProbe:
    """
    A wrapper around the inspect.signature(func).parameters object.

    Provides a subscriptable interface to the parameters of a function.
    """

    def __init__(self, func: Callable, remove_self: bool = False):
        """
        Note: `self` is not included in the parameter lists for bound method
        Is for unbound methods and functions.
        """

        self.func = func
        try:
            self.func_name = func.__name__
        except AttributeError: # Callable class
            self.func_name = func.__class__.__name__

        # Note on odd behavior:
        # class SomeClass:
        #     def some_method(self, a, b, c): ...
        #
        # inspect.signature(SomeClass().some_method).parameters.keys()
        # >>> odict_keys(['self', 'a', 'b', 'c'])
        #
        # inspect.signature(SomeClass().some_method).parameters.values()
        # >>> odict_values([<Parameter "a">, <Parameter "b">, <Parameter "c">])
        #
        # inspect.signature(SomeClass.some_method).parameters.values()
        # >>> odict_values([<Parameter "self">, <Parameter "a">, <Parameter "b">, <Parameter "c">])
        #
        # The `self` parameter isn't in the `values` of the signature of a method.
        # It is in the `values` of the signature of a function.
        parameters = dict(inspect.signature(func).parameters)
        if 'self' in parameters and remove_self:
            del parameters['self']

        # Not assigned to instance, dynamic property instead.
        parameters = tuple(
            Param(inspect_param)
            for inspect_param in parameters.values()
        )
        self._dict: Dict[str, Param] = {param.name: param for param in parameters}

    @property
    def parameters(self) -> Tuple[Param, ...]:
        """
        Dynamic so __delitem__ only have to modify self._dict
        """
        return tuple(self._dict.values())

    @property
    def instance(self) -> Any:
        """
        If the function is a bound method, this property returns the instance to
        which the method is bound.
        """
        if inspect.ismethod(self.func):
            return self.func.__self__

    def asdict(self) -> Dict[str, Param]:
        return self._dict

    @property
    def names(self) -> Tuple[str, ...]:
        return tuple(self._dict.keys())

    def _retrieve_parameters(self, key: Union[int, slice, str]) -> Tuple[Param, ...]:
        """
        Retrieve parameters based on the provided key, which can be a name, an index, a slice, or a kind.

        Description:
        -----------
        This method returns parameters based on the provided key, which can be a name, an index, a slice, or a kind.
        It tries to fetch the parameters based on the key and raises an error if the key is not found or invalid.

        Parameters:
        ----------
        key : Union[int, slice, str]
            The key to identify the parameters. Can be a name, an integer index, a slice, or a kind.

        Returns:
        -------
        Tuple[Param, ...]
            A tuple containing the matching parameters.

        Raises:
        ------
        KeyError, IndexError
            If the key is not found or invalid.

        Example:
        -------
        >>> def some_func(a, /, b, *, c): ...
        >>> probe = ParamProbe(some_func)
        >>> probe._retrieve_parameters("POSITIONAL_ONLY")
        (
            Param(name='a', kind='POSITIONAL_ONLY', default=<empty>, annotation=<empty>),
        )
        >>> probe._retrieve_parameters(1)
        (
            Param(name='b', kind='POSITIONAL_OR_KEYWORD', default=<empty>, annotation=<empty>),
        )
        >>> probe._retrieve_parameters(slice(0, 3))
        (
            Param(name='a', kind='POSITIONAL_ONLY', default=<empty>, annotation=<empty>),
            Param(name='b', kind='POSITIONAL_OR_KEYWORD', default=<empty>, annotation=<empty>),
            Param(name='c', kind='KEYWORD_ONLY', default=<empty>, annotation=<empty>)
        )
        """
        # ... Parameter index ...
        if isinstance(key, int):
            try:
                return (self.parameters[key],)
            except IndexError as e:
                raise IndexError(
                    f"Index {key} is out of range for {self.func_name} with {len(self.parameters)} parameters."
                )
        # ... Parameter slice ...
        elif isinstance(key, slice):
            try:
                return self.parameters[key]
            except IndexError as e:
                raise IndexError(
                    f"Slice {key} is out of range for {self.func_name} with {len(self.parameters)} parameters."
                )
        # ... Parameter name ...
        elif key in self._dict:
            return (self._dict[key],)
        # ... Parameter kinds ...
        elif key == "POSITIONAL_ONLY":
            return tuple(param for param in self.parameters if param.is_pos_only)
        elif key == "POSITIONAL_OR_KEYWORD":
            return tuple(param for param in self.parameters if param.is_pos_or_kw)
        elif key == "VAR_POSITIONAL":
            return tuple(param for param in self.parameters if param.is_var_pos)
        elif key == "KEYWORD_ONLY":
            return tuple(param for param in self.parameters if param.is_kw_only)
        elif key == "VAR_KEYWORD":
            return tuple(param for param in self.parameters if param.is_var_kw)
        # ... Parameter kind groups ...
        elif key == "ALL_POSITIONAL":
            return tuple(param for param in self.parameters if param.can_pass_pos_arg)
        elif key == "ALL_KEYWORD":
            return tuple(param for param in self.parameters if param.can_pass_kw_arg)
        elif key == "ALL_PARAMETERS":
            return self.parameters

        raise KeyError((
            f"Invalid key: `{key}`. "
            f"Valid keys are parameter names (for {self.func_name} these are {self.names}), "
            f"parameter kinds, which include `POSITIONAL_ONLY`, `POSITIONAL_OR_KEYWORD`, `VAR_POSITIONAL`, `KEYWORD_ONLY`, `VAR_KEYWORD`, "
            f"and parameter kind groups, which include `ALL_POSITIONAL`, `ALL_KEYWORD`, `ALL_PARAMETERS`."
        ))

    def __getitem__(self, key: str) -> Union[Param, Tuple[Param, ...]]:
        result = self._retrieve_parameters(key)

        if result == ():
            raise KeyError(key)
        elif len(result) == 1:
            return result[0]
        else:
            return result

    def __delitem__(self, key: str) -> None:
        for param in self._retrieve_parameters(key):
            del self._dict[param.name]

    def get(self, key: str, default: Any = None) -> Union[Param, Tuple[Param, ...]]:
        try:
            return self[key]
        except (IndexError, KeyError):
            return default

    def get_count(self, key: str) -> int:
        result = self.get(key, tuple())
        if isinstance(result, Param):
            return 1
        return len(result)

    def __contains__(self, key: str) -> bool:
        if not isinstance(key, str):
            return False
        return self.get(key, None) is not None

    def __len__(self) -> int:
        return len(self._dict)

    def __str__(self):
        signature = str(inspect.signature(self.func))

        if self.instance is not None:
            prepend = f"{self.instance.__class__.__name__}()."
            signature = f"(self, {signature.lstrip('(')}"
        else:
            prepend = ""

        return f"{prepend}{self.func_name}{signature}"


def mapping_to_kwargs(mapping, func):
    """
    Convert a mapping to keyword arguments suitable for a given function.

    Args:
        mapping (dict): The input mapping.
        func (callable): The function for which the keyword arguments are being prepared.

    Returns:
        dict: A dictionary of keyword arguments.
    """
    params = ParamProbe(func).names
    return {param: mapping[param] for param in params if param in mapping}
