from typing import Any, Callable, Dict, Tuple, Type, Union, Mapping, Iterable, Optional
import inspect

try:
    from .decorator_utils import export
except ImportError:
    from decorator_utils import export


EMPTY = inspect.Parameter.empty
POSITIONAL_ONLY = inspect.Parameter.POSITIONAL_ONLY
POSITIONAL_OR_KEYWORD = inspect.Parameter.POSITIONAL_OR_KEYWORD
VAR_POSITIONAL = inspect.Parameter.VAR_POSITIONAL
KEYWORD_ONLY = inspect.Parameter.KEYWORD_ONLY
VAR_KEYWORD = inspect.Parameter.VAR_KEYWORD

args_sig = inspect.Signature(
    [inspect.Parameter("args", inspect.Parameter.VAR_POSITIONAL)]
)
kwargs_sig = inspect.Signature(
    [inspect.Parameter("kwargs", inspect.Parameter.VAR_KEYWORD)]
)


@export
class Param:
    def __init__(self, inspect_param: inspect.Parameter):
        self.name: str = inspect_param.name
        self.kind: str = str(inspect_param.kind).split(".")[-1]
        self.default: Any = inspect_param.default
        self.annotation: Any = inspect_param.annotation

        self.built_in_kind: inspect.Parameter.kind = inspect_param.kind

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
            "Param("
            f'name="{self.name}", '
            f'default="{"EMPTY" if self.default is EMPTY else self.default}", '
            f'kind="{self.kind}", '
            f'annotation="{"EMPTY" if self.annotation is EMPTY else self.annotation}"'
            ")"
        )

    def __eq__(self, other):
        return (
            self.name == other.name
            and self.kind == other.kind
            and self.default == other.default
            and self.annotation == other.annotation
        )


@export
class ParamProbe:
    """
    A wrapper around the inspect.signature(func).parameters object.

    Provides a subscriptable interface to the parameters of a function.
    """

    def __init__(self, func: Callable, remove_self: bool = False):
        """
        The remove_self parameter for this constructor is only relevant for bound methods.

        >>> class SomeClass:
        ...     def __init__(self, a, b, c): ...
        ...
        ...     def some_method(self, x, y, z): ...
        ...
        >>> # unbound method
        >>> probe = ParamProbe(SomeClass.some_method)
        >>> probe.names
        ('self', 'a', 'b', 'c')
        ...
        >>> # bound method
        >>> probe = ParamProbe(SomeClass().some_method)
        >>> probe.names
        ('a', 'b', 'c')
        """

        if inspect.isclass(func):
            self.klass = func
            self.func = self.klass.__init__
            self.func_name = f"{self.klass.__name__}.__init__"
        else:  # is function, method or callable object
            try:  # function or method
                self.func = func
                self.func_name = func.__name__
            except AttributeError:  # Callable object
                self.klass = func.__class__
                self.func = func.__call__
                self.func_name = f"{self.klass.__name__}.__call__"

        parameters = dict(inspect.signature(self.func).parameters)

        # def some_func(a, b, c): ...
        # ...
        # class SomeClass:
        #     def __init__(self, a, b, c): ...
        # ...
        #     def some_method(self, x, y, z): ...

        # function signature
        # >>> str(inspect.signature(some_func))
        # '(a, b, c)'

        # __init__
        # >>> str(inspect.signature(SomeClass.__init__))
        # '(self, a, b, c)'

        # unbound method
        # >>> str(inspect.signature(SomeClass.some_method))
        # '(self, x, y, z)'

        # bound method
        # >>> str(inspect.signature(SomeClass().some_method))
        # '(x, y, z)'

        manually_add_self_parameter = False
        if ParamProbe._is_bound_method(self.func):
            # The `self` parameter is automatically removed from bound methods.
            if remove_self is True:
                ...
            else:
                manually_add_self_parameter = True
        elif ParamProbe._is_unbound_method(self.func):
            # The `self` parameter isn't automatically removed from unbound methods.
            if remove_self is True:
                del parameters[tuple(parameters.keys())[0]]
            else:
                ...
        else:
            if remove_self is True:
                raise ValueError(
                    f"Cannot remove `self` from `{self.func_name}` because it is not a method."
                )
            # no else, just pass on by

        # Not assigned to instance, dynamic property instead.
        parameters = tuple(
            Param(inspect_param) for inspect_param in parameters.values()
        )

        self._dict: Dict[str, Param] = {param.name: param for param in parameters}
        if manually_add_self_parameter is True:
            if any([param.is_pos_only for param in self._dict.values()]):
                kind = inspect.Parameter.POSITIONAL_ONLY
            else:
                kind = inspect.Parameter.POSITIONAL_OR_KEYWORD

            self._d = {
                "self": Param(inspect.Parameter("self", kind, default=self.instance))
            }
            self._d.update(self._dict)
            self._dict = self._d

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
        if ParamProbe._is_bound_method(self.func):
            return self.func.__self__

    def asdict(self) -> Dict[str, Param]:
        return self._dict

    @property
    def names(self) -> Tuple[str, ...]:
        """
        Dynamic so __delitem__ only have to modify self._dict
        """
        return tuple(self._dict.keys())

    def __getitem__(self, key: str) -> Union[Param, Tuple[Param, ...]]:
        result = self._retrieve(key)

        if result == ():
            raise KeyError(key)
        elif len(result) == 1:
            return result[0]
        else:
            return result

    def __delitem__(self, key: str) -> None:
        for param in self._retrieve(key):
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

    def __iter__(self):
        return iter(self._dict.values())

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

    # ... Private Methods ...
    def _retrieve(self, key: Union[int, slice, str]) -> Tuple[Param, ...]:
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
        >>> probe._retrieve("POSITIONAL_ONLY")
        (
            Param(name='a', kind='POSITIONAL_ONLY', default=<empty>, annotation=<empty>),
        )
        >>> probe._retrieve(1)
        (
            Param(name='b', kind='POSITIONAL_OR_KEYWORD', default=<empty>, annotation=<empty>),
        )
        >>> probe._retrieve(slice(0, 3))
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

        raise KeyError(
            (
                f"Invalid key: `{key}`. "
                f"Valid keys are parameter names (for {self.func_name} these are {self.names}), "
                f"parameter kinds, which include `POSITIONAL_ONLY`, `POSITIONAL_OR_KEYWORD`, `VAR_POSITIONAL`, `KEYWORD_ONLY`, `VAR_KEYWORD`, "
                f"and parameter kind groups, which include `ALL_POSITIONAL`, `ALL_KEYWORD`, `ALL_PARAMETERS`."
            )
        )

    @staticmethod
    def _is_bound_method(func: Callable):
        """
        Bound methods are members of a class instance.

        >>> class SomeClass:
        ...    def some_method(self): ...
        ...
        >>> ParamProbe._is_bound_method(SomeClass.some_method)
        ... False
        ...
        >>> ParamProbe._is_bound_method(SomeClass().some_method)
        ... True

        """
        return inspect.ismethod(func)

    @staticmethod
    def _is_unbound_method(func: Callable):
        """
        Unbound methods are not members of a class instance, but methods of a class.

        >>> class SomeClass:
        ...    def some_method(self): ...
        ...
        >>> ParamProbe._is_unbound_method(SomeClass.some_method)
        ... True
        ...
        >>> ParamProbe._is_unbound_method(SomeClass().some_method)
        ... False
        """

        if ParamProbe._is_bound_method(func) or not callable(func):
            return False
        return "." in func.__qualname__

    @staticmethod
    def _is_method(func: Callable):
        """
        Determine if the function is a memeber of a class or a class instance.
        """
        return ParamProbe._is_bound_method(func) or ParamProbe._is_unbound_method(func)


@export
class ArgMutator:
    """
    Subscriptable interface to the bound arguments of a function.

    Examples:
    ---------
    >>> def func(pos_only, /, pos_or_kw, *args, kw_only, **kwargs): ...
    ... mutator = ArgMutator(func, 1, 2, 3, 4, kw_only=5, var_kw1=6, var_kw2=7)
    ... mutator.args
    (1, 2, 3, 4)
    ... mutator.kwargs
    {'kw_only': 5, 'var_kw1': 6, 'var_kw2': 7}
    ... # By name ...
    ... mutator["pos_only"]
    {'pos_only': 1}
    # ... By index ...
    # Note By index, is for the parameters, not the arguments.
    ... mutator[1]
    {'pos_or_kw': 2}
    ... # By slice ...
    # Note By slice, is for the parameters, not the arguments.
    ... mutator[2:4] #
    {'args': (3, 4), 'kw_only': 5, 'kwargs': {'var_kw1': 6, 'var_kw2': 7}}
    # ... By kinds ...
    ... mutator['VAR_POSITIONAL']
    {'args': (3, 4)}
    ... mutator['VAR_KEYWORD']
    {'kwargs': {'var_kw1': 6, 'var_kw2': 7}}
    # ... By group ...
    ... mutator['ALL_POSITIONAL']
    {'pos_only': 1, 'pos_or_kw': 2, 'args': (3, 4)}
    """

    def __init__(self, func, *args, **kwargs):
        try:
            self.param_probe = ParamProbe(func, remove_self=True)
        except ValueError:
            self.param_probe = ParamProbe(func)

        self.instance = self.param_probe.instance
        self.parameters = self.param_probe.names

        self.func = self.param_probe.func
        self.func_name = self.param_probe.func_name

        # Working with methods, espically __init__ is a little tricky.
        # The easiest solution is to build a partial signature here
        # that excludes the `self` parameter. `self` can be accessed
        # via the `instance` property.
        self.sig = inspect.Signature(
            inspect.Parameter(p.name, p.built_in_kind, default=p.default)
            for p in self.param_probe
        )
        self.bound_args = self.sig.bind(*args, **kwargs)
        self.bound_args.apply_defaults()
        self._bound_arg_dict = dict(self.bound_args.arguments)

        # Names of parameters, and how they were passed
        self.pos_keys, self.kw_keys = [], []
        for param in self.param_probe:
            if param.is_pos_only:
                self.pos_keys.append(param.name)

            # Split this up, correctly
            elif param.is_pos_or_kw:
                if param.name in kwargs:
                    self.kw_keys.append(param.name)
                else:
                    self.pos_keys.append(param.name)

            elif param.is_var_pos:
                self.pos_keys.append(param.name)
            elif param.is_kw_only:
                self.kw_keys.append(param.name)
            elif param.is_var_kw:
                self.kw_keys.append(param.name)
        self.pos_keys, self.kw_keys = tuple(self.pos_keys), tuple(self.kw_keys)

        # Easier subscripting
        try:
            self.var_pos_param = self.param_probe["VAR_POSITIONAL"].name
        except KeyError:
            self.var_pos_param = None

        try:
            self.var_kw_param = self.param_probe["VAR_KEYWORD"].name
        except KeyError:
            self.var_kw_param = None

        # Useful partial signatures
        self.pos_sig = inspect.Signature(
            inspect.Parameter(p.name, p.built_in_kind, default=p.default)
            for p in self.param_probe
            if p.name in self.pos_keys
        )
        self.kw_sig = inspect.Signature(
            inspect.Parameter(p.name, p.built_in_kind, default=p.default)
            for p in self.param_probe
            if p.name in self.kw_keys
        )

    @property
    def values(self) -> Tuple[Any, ...]:
        """
        Return a tuple of arguments passed to the function.

        For a tuple of positional arguments, use `args`.
        For a dict of keyword arguments, use `kwargs`.
        """
        result = []
        for key, value in self._bound_arg_dict.items():
            if key == self.var_pos_param:
                result.extend(value)
            elif key == self.var_kw_param:
                result.extend(value.values())
            else:
                result.append(value)
        return tuple(result)

    def asdict(self) -> Dict[str, Any]:
        """
        Return a dict of arguments passed to the function.
        Parameter names are keys and arguments are values.
        """
        return self._bound_arg_dict

    # ... Args & Kwargs ...
    @property
    def args(self) -> Tuple[Any, ...]:
        """
        Return a tuple of arguments passed positionally to the function.
        """
        result = []
        for name in self.pos_keys:
            if name == self.var_pos_param:
                result.extend(self._bound_arg_dict[name])
            else:
                result.append(self._bound_arg_dict[name])
        return tuple(result)

    @args.setter
    def args(self, values: Iterable[Any]) -> None:
        bound_args = self.pos_sig.bind(*values)
        bound_args.apply_defaults()

        for key, value in dict(bound_args.arguments).items():
            self._bound_arg_dict[key] = value

    @property
    def kwargs(self) -> Dict[str, Any]:
        """
        Return a dict of arguments passed as keyword arguments to the function.
        """
        result = {}
        for name in self.kw_keys:
            if name == self.var_kw_param:
                result.update(self._bound_arg_dict[name])
            else:
                result[name] = self._bound_arg_dict[name]
        return result

    @kwargs.setter
    def kwargs(self, values: Dict[str, Any]) -> None:
        bound_args = self.kw_sig.bind(**values)
        bound_args.apply_defaults()

        for key, value in dict(bound_args.arguments).items():
            self._bound_arg_dict[key] = value

    # ... Dunder methods ...
    def __contains__(self, parameter_name: str) -> bool:
        """
        If the function contains a parameter with the given name, return True.
        """
        return parameter_name in self.parameters

    def __len__(self):
        return len(self._bound_arg_dict)

    def __str__(self):
        return f"<ArgMutator: {str(self.param_probe)}>"

    # ... Private methods ...
    def _get_parameter_names_from_key(
        self, key: Union[int, slice, str]
    ) -> Tuple[str, ...]:
        if isinstance(key, int):  # IndexError
            param_names = [self.parameters[key]]
        elif isinstance(key, slice):  # IndexError
            param_names = self.parameters[key]
        elif key == "ALL_POSITIONAL":
            param_names = self.pos_keys
        elif key == "VAR_POSITIONAL":
            param_names = [self.var_pos_param]
        elif key == "ALL_KEYWORD":
            param_names = self.kw_keys + tuple(
                self._bound_arg_dict[self.var_kw_param].keys()
            )
        elif key == "VAR_KEYWORD":
            param_names = [self.var_kw_param]
        elif key == "NESTED_VAR_KEYWORDS":
            param_names = self._bound_arg_dict[self.var_kw_param].keys()
        elif key == "ALL_ARGUMENTS":
            param_names = self.parameters
        elif key in self._bound_arg_dict:
            param_names = [key]
        elif key in self.kwargs:
            param_names = [key]
        else:
            raise KeyError()
        return tuple(param_names)

    def _get_argument_value(self, name: str) -> Any:
        """
        Retrieve the argument value for the given name.

        Search the bound arguments, and if not found
        searches the variable keyword arguments.
        """
        try:
            return self._bound_arg_dict[name]
        except KeyError:
            return self._bound_arg_dict[self.var_kw_param][name]

    def _set_argument_value(self, name: str, value: Any) -> None:
        """Set the argument value for the given name."""
        if name == self.var_pos_param:  # Set directly as args
            if not isinstance(value, Iterable):
                raise TypeError(
                    f"Variable positional arguments must be an Iterable, not {type(value)}."
                )
        elif name == self.var_kw_param:  # Set directly as kwargs
            if not isinstance(value, Mapping):
                raise TypeError(
                    f"Variable keyword arguments must be a Mapping, not {type(value)}."
                )

        # Named parameters
        if name in self.parameters:
            self._bound_arg_dict[name] = value

        # If variable keyword arguments can be passed, we can either
        # change the value of a current argument, or add a new argument.
        elif self.var_kw_param is not None:
            self._bound_arg_dict[self.var_kw_param][name] = value

        else:
            raise KeyError(f"Unexpected keyword argument: {name}")

    # ... Subscriptable interface / Similar methods ...
    def __getitem__(self, key: Union[int, slice, str]) -> Dict[str, Any]:
        """
        Returns a dictionary, as it makes it easier to set values.

        >>> for key, value in mutator["ALL_ARGUMENTS"].items():
        ...    mutator[key] = f"{value} was passed to {key}"
        """
        try:
            return {
                parameter_name: self._get_argument_value(parameter_name)
                for parameter_name in self._get_parameter_names_from_key(key)
            }
        except (IndexError, KeyError):
            raise KeyError(
                (
                    f"Invalid key: `{key}`. "
                    f"Valid keys are either parameter names (for {self.func_name} these are {', '.join(self.parameters)}), "
                    f"or argument kinds, which include `ALL_POSITIONAL`, `VAR_POSITIONAL`, `ALL_KEYWORD`, `VAR_KEYWORD`, `NESTED_VAR_KEYWORD` or `ALL_ARGUMENTS`."
                )
            )

    def get(
        self, key: Union[int, slice, str], args_only: bool = False, default: Any = None
    ) -> Union[Dict[str, Any], Tuple[Any, ...]]:
        try:
            d = self[key]
            if args_only:
                return tuple(d.values())
            return d
        except (IndexError, KeyError):
            return default

    def __setitem__(
        self,
        key: Union[int, slice, str],
        value: Union[Any, Tuple[Any, ...], Dict[str, Any]],
    ) -> None:
        """
        Set the value for one or more arguments.

        Parameters:
        -----------
        - key : str
            The name or kind of the argument(s) to set.
        - value : Union[Any, Tuple[Any, ...], Dict[str, Any]]
            The value to set for the argument(s).

        Raises:
        -------
        - KeyError
            If the key does not match any parameter names or kinds.
        - ValueError
            If too few or too many arguments are passed.
        - TypeError
            If a tuple is not passed for a variable positional argument.
            If a dict is not passed for a variable keyword argument.

        Note:
        -----
        Only either positional arguments or keyword arguments can be updated at once.
        The 'ALL_ARGUMENTS' key is not supported for setting with this method.
        If a slice is passed, the slice cannot contain both positional and keyword arguments.

        Examples:
        ---------
        >>> def func(a, b, c): ...
        >>> mutator = ArgMutator(func, 1, 2, 3)
        >>> mutator.args
        (1, 2, 3)
        >>> mutator.kwargs
        {}

        >>> mutator["a"] = 4
        >>> mutator.args
        (4, 2, 3)
        >>> mutator["ALL_POSITIONAL"] = (5, 6, 7)
        >>> mutator.args
        (5, 6, 7)
        >>> mutator["ALL_KEYWORDS"] = {"a": 8, "b": 9, "c": 10}
        ... ValueError: No keyword arguments were passed to the function.
        >>> mutator["ALL_ARGUMENTS"] = (11, 12, 13)
        >>> mutator.args
        (11, 12, 13)

        >>> def func(pos_only, /, pos_or_kw, *var_pos, kw_only, **var_kw): ...
        >>> mutator = ArgMutator(func, 1, 2, 3, 4, kw_only=5, var_kw1=6, var_kw2=7)
        >>> mutator.args
        (1, 2, 3, 4)
        >>> mutator.kwargs
        {'kw_only': 5, 'var_kw1': 6, 'var_kw2': 7}
        >>> mutator["var_pos"] = (8, 9)
        >>> mutator.args
        (1, 2, 8, 9)
        >>> mutator["var_kw"] = {'var_kw1': 10, 'var_kw2': 11}
        >>> mutator.kwargs
        {'kw_only': 5, 'var_kw1': 10, 'var_kw2': 11}
        >>> mutator["ALL_POSITIONAL"] = (12, 13, 14, 15)
        >>> mutator.args
        (12, 13, 14, 15)
        >>> mutator["ALL_KEYWORDS"] = {'kw_only': 16, 'var_kw1': 17, 'var_kw2': 18}
        >>> mutator.kwargs
        {'kw_only': 16, 'var_kw1': 17, 'var_kw2': 18}
        """

        try:
            name, *other = self._get_parameter_names_from_key(key)
        except (IndexError, KeyError):
            raise KeyError(
                (
                    f"Invalid key: `{key}`. "
                    f"Valid keys are either parameter names (for {self.func_name} these are {', '.join(self.parameters)}), "
                    f"or argument kinds, which include `VAR_POSITIONAL` or `VAR_KEYWORD`, when settings values."
                )
            )

        if other:
            raise ValueError(
                (
                    "A key must correspond to a single parameter name, when settings values. "
                    f"`{key}` corresponds to {len(other) + 1} parameter names ({', '.join(self._get_parameter_names_from_key(key))})."
                )
            )

        self._set_argument_value(name, value)

    @staticmethod
    def bind(func, *args, **kwargs) -> Dict[str, Any]:
        try:
            param_probe = ParamProbe(func, remove_self=True)
        except ValueError:
            param_probe = ParamProbe(func)

        sig = inspect.Signature(
            inspect.Parameter(p.name, p.built_in_kind, default=p.default)
            for p in param_probe
        )

        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()
        return dict(bound_args.arguments)

    @staticmethod
    def missing_args(func, *args, **kwargs) -> Tuple[str, ...]:
        try:
            param_probe = ParamProbe(func, remove_self=True)
        except ValueError:
            param_probe = ParamProbe(func)

        missing_params = list(param_probe.names)

        for _ in range(len(args)):
            missing_params.pop(0)

        for key in kwargs:
            missing_params.remove(key)

        # VAR_POSITIONAL and VAR_KEYWORD are not required
        for key in ("VAR_POSITIONAL", "VAR_KEYWORD"):
            try:
                missing_params.remove(param_probe[key].name)
            except (KeyError, ValueError):
                ...

        # Remove parameters with default values
        for param in missing_params:
            if param_probe[param].default is not EMPTY:
                missing_params.remove(param)

        return tuple(missing_params)


@export
def bind_args(func, *args, **kwargs) -> Dict[str, Any]:
    return ArgMutator.bind(func, *args, **kwargs)


@export
def missing_args(func, *args, **kwargs) -> Tuple[str, ...]:
    return ArgMutator.missing_args(func, *args, **kwargs)


@export
def build_signature(
    pos_only: Tuple[str, ...] = tuple(),
    pos_or_kw: Tuple[str, ...] = tuple(),
    var_pos: str = None,
    kw_only: Tuple[str, ...] = tuple(),
    var_kw: str = None,
    bind_args: Optional[Tuple[Any, ...]] = None,
    bind_kwargs: Optional[Dict[str, Any]] = None,
) -> Union[inspect.Signature, Dict[str, Any]]:
    """
    Build a signature from the provided parameters.

    You cannot call a signature, but can bind it to arguments.

    Example:
    --------
    >>> sig = build_signature(pos_or_kw('a', 'b', 'c'))
    >>> sig.bind(1, 2, 3).arguments
    {'a': 1, 'b': 2, 'c': 3}
    """
    parameters = []
    for name in pos_only:
        parameters.append(inspect.Parameter(name, inspect.Parameter.POSITIONAL_ONLY))
    for name in pos_or_kw:
        parameters.append(
            inspect.Parameter(name, inspect.Parameter.POSITIONAL_OR_KEYWORD)
        )
    if var_pos is not None:
        parameters.append(inspect.Parameter(var_pos, inspect.Parameter.VAR_POSITIONAL))
    for name in kw_only:
        parameters.append(inspect.Parameter(name, inspect.Parameter.KEYWORD_ONLY))
    if var_kw is not None:
        parameters.append(inspect.Parameter(var_kw, inspect.Parameter.VAR_KEYWORD))
    sig = inspect.Signature(parameters)

    if bind_args is None and bind_kwargs is None:
        return sig
    elif bind_args is not None and bind_kwargs is None:
        return sig.bind(*bind_args).arguments
    elif bind_args is None and bind_kwargs is not None:
        return sig.bind(**bind_kwargs).arguments
    else:
        args = bind_args or tuple()
        kwargs = bind_kwargs or dict()

        return sig.bind(*args, **kwargs).arguments


@export
def mapping_to_kwargs(func: Union[Type, Callable], mapping: Mapping):
    """
    Convert a mapping to keyword arguments suitable for a given function.

    Args:
        mapping (dict): The input mapping.
        func (callable): The function for which the keyword arguments are being prepared.

    Returns:
        dict: A dictionary of keyword arguments.
    """
    try:
        params = ParamProbe(func, remove_self=True).names
    except ValueError:
        params = ParamProbe(func).names

    return {param: mapping[param] for param in params if param in mapping}
