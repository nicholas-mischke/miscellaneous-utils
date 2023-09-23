import pytest
from miscellaneous_utilities.params import (
    Param,
    ParamProbe,
    ArgMutator,
    mapping_to_kwargs,
)

from pathlib import Path
import sys

# Import from the tests/_signatures.py file
sys.path.append(str(Path(__file__).parent))
from _signatures import (
    some_func,
    many_params,
    SomeClass,
    some_instance,
)


class TestParamProbe:
    # ... Setup fixtures ...
    @pytest.fixture
    def probe(self, some_func):
        return ParamProbe(some_func)

    @pytest.fixture
    def constructor_probe(self, some_constructor):
        return ParamProbe(some_constructor, remove_self=True)

    @pytest.fixture
    def method_probe(self, some_method):
        return ParamProbe(some_method, remove_self=True)

    @pytest.fixture
    def callable_class_probe(self, some_callable_class):
        return ParamProbe(some_callable_class, remove_self=True)

    # ... Tests ...
    @pytest.mark.parametrize(
        "func, remove_self, expected",
        [
            # function that's not a method
            (some_func, False, ("a", "b", "c")),
            (some_func, True, ValueError),
            # __init__ which is a special case
            (SomeClass, False, ("self", "a", "b", "c")),
            (SomeClass, True, ("a", "b", "c")),
            # bound method
            (some_instance.some_method, False, ("self", "some_param")),
            (some_instance.some_method, True, ("some_param",)),
            # unbound method
            (SomeClass.some_method, False, ("self", "some_param")),
            (SomeClass.some_method, True, ("some_param",)),
        ],
    )
    def test_remove_self(self, func, remove_self, expected):
        if expected == ValueError:
            with pytest.raises(ValueError):
                ParamProbe(func, remove_self=remove_self)
        else:
            assert ParamProbe(func, remove_self=remove_self).names == expected

    def test_func_name(
        self, probe, constructor_probe, method_probe, callable_class_probe
    ):
        assert probe.func_name == "some_func"
        assert constructor_probe.func_name == "SomeClass.__init__"
        assert method_probe.func_name == "some_method"
        assert callable_class_probe.func_name == "SomeClass.__call__"

    def test_instance(
        self, probe, constructor_probe, method_probe, callable_class_probe
    ):
        assert probe.instance == None
        assert constructor_probe.instance == None
        assert str(method_probe.instance.__class__.__name__) == "SomeClass"
        assert str(callable_class_probe.instance.__class__.__name__) == "SomeClass"

    def test_names(self, probe, constructor_probe, method_probe, callable_class_probe):
        """
        `self` is removed from the list of parameters
        the instance can be accessed via `instance` property
        """
        names = (
            "pos_only_param",
            "pos_or_kw_param",
            "var_pos_param",
            "kw_only_param",
            "var_kw_param",
        )
        assert probe.names == names
        assert constructor_probe.names == names
        assert method_probe.names == names
        assert callable_class_probe.names == names

    def test_retrieve(self, probe, method_probe):
        for probe in (probe, method_probe):
            # ... Parameter index ...
            assert probe._retrieve(0)[0].name == "pos_only_param"
            assert probe._retrieve(1)[0].name == "pos_or_kw_param"
            assert probe._retrieve(2)[0].name == "var_pos_param"
            assert probe._retrieve(3)[0].name == "kw_only_param"
            assert probe._retrieve(4)[0].name == "var_kw_param"

            # ... Parameter slice ...
            assert tuple(p.name for p in probe._retrieve(slice(1, 3))) == (
                "pos_or_kw_param",
                "var_pos_param",
            )

            # ... Parameter name ...
            assert probe._retrieve("pos_only_param")[0].name == "pos_only_param"
            assert probe._retrieve("pos_or_kw_param")[0].name == "pos_or_kw_param"
            assert probe._retrieve("var_pos_param")[0].name == "var_pos_param"
            assert probe._retrieve("kw_only_param")[0].name == "kw_only_param"
            assert probe._retrieve("var_kw_param")[0].name == "var_kw_param"

            # ... Parameter kinds ...
            assert tuple(p.name for p in probe._retrieve("POSITIONAL_ONLY")) == (
                "pos_only_param",
            )
            assert tuple(p.name for p in probe._retrieve("POSITIONAL_OR_KEYWORD")) == (
                "pos_or_kw_param",
            )
            assert tuple(p.name for p in probe._retrieve("VAR_POSITIONAL")) == (
                "var_pos_param",
            )
            assert tuple(p.name for p in probe._retrieve("KEYWORD_ONLY")) == (
                "kw_only_param",
            )
            assert tuple(p.name for p in probe._retrieve("VAR_KEYWORD")) == (
                "var_kw_param",
            )

            # ... Parameter kind groups ...
            assert tuple(p.name for p in probe._retrieve("ALL_POSITIONAL")) == (
                "pos_only_param",
                "pos_or_kw_param",
                "var_pos_param",
            )
            assert tuple(p.name for p in probe._retrieve("ALL_KEYWORD")) == (
                "pos_or_kw_param",
                "kw_only_param",
                "var_kw_param",
            )
            assert tuple(p.name for p in probe._retrieve("ALL_PARAMETERS")) == (
                "pos_only_param",
                "pos_or_kw_param",
                "var_pos_param",
                "kw_only_param",
                "var_kw_param",
            )

    def test__getitem__(self, probe):
        assert probe["pos_only_param"].name == "pos_only_param"

    def test__delitem__(self, probe):
        assert len(probe._dict) == 5
        del probe["pos_only_param"]
        assert len(probe._dict) == 4
        del probe["pos_or_kw_param"]
        assert len(probe._dict) == 3
        del probe["var_pos_param"]
        assert len(probe._dict) == 2
        del probe["kw_only_param"]
        assert len(probe._dict) == 1
        del probe["var_kw_param"]
        assert len(probe._dict) == 0

        with pytest.raises(KeyError):
            del probe["not_a_param"]

    def test_get_count(self, probe):
        assert probe.get_count("POSITIONAL_ONLY") == 1
        assert probe.get_count("POSITIONAL_OR_KEYWORD") == 1
        assert probe.get_count("VAR_POSITIONAL") == 1
        assert probe.get_count("KEYWORD_ONLY") == 1
        assert probe.get_count("VAR_KEYWORD") == 1

    def test__contains__(self, probe):
        assert "pos_only_param" in probe
        assert "not_a_param" not in probe

    def test__len__(self, probe):
        assert len(probe) == 5

    def test__str__(self, probe, method_probe):
        assert (
            str(probe)
            == "some_func(pos_only_param, /, pos_or_kw_param, *var_pos_param, kw_only_param, **var_kw_param)"
        )
        assert (
            str(method_probe)
            == "SomeClass().some_method(self, pos_only_param, /, pos_or_kw_param, *var_pos_param, kw_only_param, **var_kw_param)"
        )


class TestArgMutator:
    @pytest.fixture
    def mutator(self):
        return ArgMutator(
            many_params,
            # positional
            1,
            2,
            # var positional
            "a",
            "b",
            "c",
            # keyword only
            kw_only_param="kw_only_arg",
            # var keyword
            kw1="kw1_arg",
            kw2="kw2_arg",
        )

    @pytest.fixture
    def simple_mutator(self):
        return ArgMutator(some_func, 1, 2, 3)

    @pytest.mark.parametrize(
        "func, args, kwargs, expected_dict",
        [
            (
                some_func,
                (1, 2),
                {"c": 3},
                {
                    "instance": None,
                    "parameters": ("a", "b", "c"),
                    "func": some_func,
                    "func_name": "some_func",
                    "sig": "(a, b, c)",
                    "_bound_arg_dict": {"a": 1, "b": 2, "c": 3},
                    "pos_keys": ("a", "b"),
                    "kw_keys": ("c",),
                    "var_pos_param": None,
                    "var_kw_param": None,
                    "pos_sig": "(a, b)",
                    "kw_sig": "(c)",
                },
            ),
            (
                many_params,
                (1,),
                {"pos_or_kw_param": 2, "kw_only_param": 3},
                {
                    "instance": None,
                    "parameters": (
                        "pos_only_param",
                        "pos_or_kw_param",
                        "var_pos_param",
                        "kw_only_param",
                        "var_kw_param",
                    ),
                    "func": many_params,
                    "func_name": "many_params",
                    "sig": "(pos_only_param, /, pos_or_kw_param, *var_pos_param, kw_only_param, **var_kw_param)",
                    "_bound_arg_dict": {
                        "pos_only_param": 1,
                        "pos_or_kw_param": 2,
                        "var_pos_param": (),
                        "kw_only_param": 3,
                        "var_kw_param": {},
                    },
                    "pos_keys": ("pos_only_param", "var_pos_param"),
                    "kw_keys": ("pos_or_kw_param", "kw_only_param", "var_kw_param"),
                    "var_pos_param": "var_pos_param",
                    "var_kw_param": "var_kw_param",
                    "pos_sig": "(pos_only_param, /, *var_pos_param)",
                    "kw_sig": "(pos_or_kw_param, *, kw_only_param, **var_kw_param)",
                },
            ),
            (
                SomeClass,
                (1, 2),
                {"c": 3},
                {
                    "instance": None,
                    "parameters": ("a", "b", "c"),
                    "func": SomeClass.__init__,
                    "func_name": "SomeClass.__init__",
                    "sig": "(a, b, c)",
                    "_bound_arg_dict": {"a": 1, "b": 2, "c": 3},
                    "pos_keys": ("a", "b"),
                    "kw_keys": ("c",),
                    "var_pos_param": None,
                    "var_kw_param": None,
                    "pos_sig": "(a, b)",
                    "kw_sig": "(c)",
                },
            ),
            (
                some_instance.many_params,
                (1, 2, "x", "y", "z"),
                {
                    "kw_only_param": 3,
                    "english_greeting": "hello",
                    "french_greeting": "bonjour",
                },
                {
                    "instance": "Not None",
                    "parameters": (
                        "pos_only_param",
                        "pos_or_kw_param",
                        "var_pos_param",
                        "kw_only_param",
                        "var_kw_param",
                    ),
                    "func": some_instance.many_params,
                    "func_name": "many_params",
                    "sig": "(pos_only_param, /, pos_or_kw_param, *var_pos_param, kw_only_param, **var_kw_param)",
                    "_bound_arg_dict": {
                        "pos_only_param": 1,
                        "pos_or_kw_param": 2,
                        "var_pos_param": ("x", "y", "z"),
                        "kw_only_param": 3,
                        "var_kw_param": {
                            "english_greeting": "hello",
                            "french_greeting": "bonjour",
                        },
                    },
                    "pos_keys": ("pos_only_param", "pos_or_kw_param", "var_pos_param"),
                    "kw_keys": ("kw_only_param", "var_kw_param"),
                    "var_pos_param": "var_pos_param",
                    "var_kw_param": "var_kw_param",
                    "pos_sig": "(pos_only_param, /, pos_or_kw_param, *var_pos_param)",
                    "kw_sig": "(*, kw_only_param, **var_kw_param)",
                },
            ),
        ],
    )
    def test_constructor(self, func, args, kwargs, expected_dict):
        mutator = ArgMutator(func, *args, **kwargs)

        for key, value in expected_dict.items():
            if key == "instance":
                if value is None:
                    assert mutator.instance is None
                else:
                    assert mutator.instance is not None

            else:
                mutator_value = getattr(mutator, key)
                if isinstance(value, str):
                    mutator_value = str(mutator_value)

                assert mutator_value == value

    def test_values(self, mutator):
        assert mutator.values == (1, 2, "a", "b", "c", "kw_only_arg", "kw1_arg", "kw2_arg")

    def test_asdict(self, mutator):
        assert mutator.asdict() == {
            "pos_only_param": 1,
            "pos_or_kw_param": 2,
            "var_pos_param": ("a", "b", "c"),
            "kw_only_param": "kw_only_arg",
            "var_kw_param": {"kw1": "kw1_arg", "kw2": "kw2_arg"},
        }

    def test_args(self, mutator):
        # getter
        assert mutator.args == (1, 2, "a", "b", "c")

        # setter
        mutator.args = (10, 20, "x", "y", "z")
        assert mutator._bound_arg_dict == {
            "pos_only_param": 10,
            "pos_or_kw_param": 20,
            "var_pos_param": ("x", "y", "z"),
            "kw_only_param": "kw_only_arg",
            "var_kw_param": {"kw1": "kw1_arg", "kw2": "kw2_arg"},
        }
        assert mutator.args == (10, 20, "x", "y", "z")

    def test_kwargs(self, mutator):
        # getter
        assert mutator.kwargs == {
            "kw_only_param": "kw_only_arg",
            "kw1": "kw1_arg",
            "kw2": "kw2_arg",
        }

        # setter
        mutator.kwargs = {
            "kw_only_param": "new_kw_only_arg",
            "kw1": "new_kw1_arg",
            "kw2": "new_kw2_arg",
            "another_kw": "another_kw_arg",
        }
        assert mutator._bound_arg_dict == {
            "pos_only_param": 1,
            "pos_or_kw_param": 2,
            "var_pos_param": ("a", "b", "c"),
            "kw_only_param": "new_kw_only_arg",
            "var_kw_param": {
                "kw1": "new_kw1_arg",
                "kw2": "new_kw2_arg",
                "another_kw": "another_kw_arg",
            },
        }
        assert mutator.kwargs == {
            "kw_only_param": "new_kw_only_arg",
            "kw1": "new_kw1_arg",
            "kw2": "new_kw2_arg",
            "another_kw": "another_kw_arg",
        }

    def test_contains(self, mutator):
        assert 'pos_only_param' in mutator
        assert 'not_a_param' not in mutator

    def test_len(self, mutator):
        assert len(mutator) == 5

    def test_str(self, mutator):
        assert str(mutator) == "<ArgMutator: many_params(pos_only_param, /, pos_or_kw_param, *var_pos_param, kw_only_param, **var_kw_param)>"

    @pytest.mark.parametrize(
        "key, expected_names",
        [
            # Using integer index
            (0, ("pos_only_param",)),
            # Using slice
            (slice(0, 2), ("pos_only_param", "pos_or_kw_param")),
            # Using parameter kinds
            ("ALL_POSITIONAL", ("pos_only_param", "pos_or_kw_param", "var_pos_param")),
            ("VAR_POSITIONAL", ("var_pos_param",)),
            ("ALL_KEYWORD", ("kw_only_param", "var_kw_param", "kw1", "kw2")),
            ("VAR_KEYWORD", ("var_kw_param",)),
            ("NESTED_VAR_KEYWORDS", ("kw1", "kw2")),
            # Using parameter names (non nested kwargs)
            ("kw_only_param", ("kw_only_param",)),
            # Using nested kwargs
            ("kw1", ("kw1",)),
        ],
    )
    def test_get_parameter_names_from_key(self, mutator, key, expected_names):
        assert mutator._get_parameter_names_from_key(key) == expected_names

    @pytest.mark.parametrize(
        "name, expected_value",
        [
            ("pos_only_param", 1),
            ("var_pos_param", ("a", "b", "c")),
            ("var_kw_param", {"kw1": "kw1_arg", "kw2": "kw2_arg"}),
            ("kw1", "kw1_arg"),
        ],
    )
    def test_get_argument_value(self, mutator, name, expected_value):
        assert mutator._get_argument_value(name) == expected_value

    @pytest.mark.parametrize(
        "name, value, expected_dict",
        [
            ("pos_only_param", 100, {
                'pos_only_param': 100,
                'pos_or_kw_param': 2,
                'var_pos_param': ('a', 'b', 'c'),
                'kw_only_param': 'kw_only_arg',
                'var_kw_param': {'kw1': 'kw1_arg', 'kw2': 'kw2_arg'}
            }),
            ("var_pos_param", ("x", "y", "z"), {
                'pos_only_param': 1,
                'pos_or_kw_param': 2,
                'var_pos_param': ('x', 'y', 'z'),
                'kw_only_param': 'kw_only_arg',
                'var_kw_param': {'kw1': 'kw1_arg', 'kw2': 'kw2_arg'}
            }),
            ("var_kw_param", {"kw1": "new_kw1_arg", "kw2": "new_kw2_arg"}, {
                'pos_only_param': 1,
                'pos_or_kw_param': 2,
                'var_pos_param': ('a', 'b', 'c'),
                'kw_only_param': 'kw_only_arg',
                'var_kw_param': {"kw1": "new_kw1_arg", "kw2": "new_kw2_arg"}
            }),
            ("new_var_kw_param", "new_var_kw_param_value", {
                'pos_only_param': 1,
                'pos_or_kw_param': 2,
                'var_pos_param': ('a', 'b', 'c'),
                'kw_only_param': 'kw_only_arg',
                'var_kw_param': {
                    'kw1': 'kw1_arg',
                    'kw2': 'kw2_arg',
                    "new_var_kw_param": "new_var_kw_param_value"
                }
            }),
        ],
    )
    def test_set_argument_value(self, mutator, name, value, expected_dict):
        mutator._set_argument_value(name, value)
        assert mutator._bound_arg_dict == expected_dict

    @pytest.mark.parametrize(
        "key, expected", [
            (100, KeyError),
            (0, {"pos_only_param": 1}),
            (slice(0, 4, 2), {"pos_only_param": 1, "var_pos_param": ("a", "b", "c")}),
            ("ALL_POSITIONAL", {"pos_only_param": 1, "pos_or_kw_param": 2, "var_pos_param": ("a", "b", "c")}),
            ("ALL_KEYWORD", {"kw_only_param": "kw_only_arg", "var_kw_param": {"kw1": "kw1_arg", "kw2": "kw2_arg"}, "kw1": "kw1_arg", "kw2": "kw2_arg"}),
            ("NESTED_VAR_KEYWORDS", {"kw1": "kw1_arg", "kw2": "kw2_arg"}),
        ]
    )
    def test__getitem__(self, mutator, key, expected):
        if expected == KeyError:
            with pytest.raises(KeyError):
                mutator[key]
        else:
            assert mutator[key] == expected

    @pytest.mark.parametrize(
        "key, args_only, default, expected", [
            (100, False, "Key Not Present", "Key Not Present"),
            ("ALL_KEYWORD", True, None, ("kw_only_arg", {"kw1": "kw1_arg", "kw2": "kw2_arg"}, "kw1_arg", "kw2_arg")),
            ("VAR_POSITIONAL", False, None, {'var_pos_param': ('a', 'b', 'c')}),
        ]
    )
    def test_get(self, mutator, key, args_only, default, expected):
        assert mutator.get(key, args_only, default) == expected

    @pytest.mark.parametrize("key, value, error, expected", [
        (100, "new_value", KeyError, None),
        ("ALL_POSITIONAL", "new_value", ValueError, None),
        ("a", 100, None, {'a': 100, 'b': 2, 'c': 3}),
    ])
    def test__setitem__(self, simple_mutator, key, value, error, expected):
        if error:
            with pytest.raises(error):
                simple_mutator[key] = value
        else:
            simple_mutator[key] = value
            assert simple_mutator._bound_arg_dict == expected

    def test_bind(self):
        assert ArgMutator.bind(some_func, 1, 2, 3) == {"a": 1, "b": 2, "c": 3}


def test_mapping_to_kwargs():
    mapping_one = {"a": 1, "b": 2, "c": 3, "d": 4}
    mapping_two = {"a": 1, "b": 2}

    assert mapping_to_kwargs(some_func, mapping_one) == {"a": 1, "b": 2, "c": 3}
    assert mapping_to_kwargs(SomeClass, mapping_one) == {"a": 1, "b": 2, "c": 3}

    assert mapping_to_kwargs(some_func, mapping_two) == {"a": 1, "b": 2}
    assert mapping_to_kwargs(SomeClass, mapping_two) == {"a": 1, "b": 2}


if __name__ == "__main__":
    from pathlib import Path
    from pprint import pprint

    path = Path(__file__).absolute()

    pytest.main([str(path)])
    # pytest.main([f"{str(path)}::TestParamProbe", "-s"])
    # pytest.main([f"{str(path)}::TestArgMutator", "-vv"])
