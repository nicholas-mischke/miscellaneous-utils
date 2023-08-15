import pytest
from utils.params import Param, ParamProbe, mapping_to_kwargs


class TestParamProbe:
    @pytest.fixture
    def probe(self, some_func):
        return ParamProbe(some_func)

    @pytest.fixture
    def method_probe(self, some_method):
        return ParamProbe(some_method)

    def test_instance(self, probe, method_probe):
        assert probe.instance is None
        assert str(method_probe.instance.__class__.__name__) == "SomeClass"

    def test_names(self, probe, method_probe):
        """
        `self` is removed from the list of parameters
        the instance can be accessed via `instance` property
        """
        names = ("pos_only", "pos_or_kw", "var_pos", "kw_only", "var_kw")
        assert probe.names == names
        assert method_probe.names == names

    def test_retrieve_parameters(self, probe, method_probe):
        for probe in (probe, method_probe):
            # ... Parameter index ...
            assert probe._retrieve_parameters(0)[0].name == "pos_only"
            assert probe._retrieve_parameters(1)[0].name == "pos_or_kw"
            assert probe._retrieve_parameters(2)[0].name == "var_pos"
            assert probe._retrieve_parameters(3)[0].name == "kw_only"
            assert probe._retrieve_parameters(4)[0].name == "var_kw"

            # ... Parameter slice ...
            assert tuple(p.name for p in probe._retrieve_parameters(slice(1, 3))) == (
                "pos_or_kw",
                "var_pos",
            )

            # ... Parameter name ...
            assert probe._retrieve_parameters("pos_only")[0].name == "pos_only"
            assert probe._retrieve_parameters("pos_or_kw")[0].name == "pos_or_kw"
            assert probe._retrieve_parameters("var_pos")[0].name == "var_pos"
            assert probe._retrieve_parameters("kw_only")[0].name == "kw_only"
            assert probe._retrieve_parameters("var_kw")[0].name == "var_kw"

            # ... Parameter kinds ...
            assert tuple(p.name for p in probe._retrieve_parameters("POSITIONAL_ONLY")) == (
                "pos_only",
            )
            assert tuple(
                p.name for p in probe._retrieve_parameters("POSITIONAL_OR_KEYWORD")
            ) == ("pos_or_kw",)
            assert tuple(p.name for p in probe._retrieve_parameters("VAR_POSITIONAL")) == (
                "var_pos",
            )
            assert tuple(p.name for p in probe._retrieve_parameters("KEYWORD_ONLY")) == (
                "kw_only",
            )
            assert tuple(p.name for p in probe._retrieve_parameters("VAR_KEYWORD")) == (
                "var_kw",
            )

            # ... Parameter kind groups ...
            assert tuple(p.name for p in probe._retrieve_parameters("ALL_POSITIONAL")) == (
                "pos_only",
                "pos_or_kw",
                "var_pos",
            )
            assert tuple(p.name for p in probe._retrieve_parameters("ALL_KEYWORD")) == (
                "pos_or_kw",
                "kw_only",
                "var_kw",
            )
            assert tuple(p.name for p in probe._retrieve_parameters("ALL_PARAMETERS")) == (
                "pos_only",
                "pos_or_kw",
                "var_pos",
                "kw_only",
                "var_kw",
            )

    def test__getitem__(self, probe):
        assert probe["pos_only"].name == "pos_only"

    def test__delitem__(self, probe):
        assert len(probe._dict) == 5
        del probe["pos_only"]
        assert len(probe._dict) == 4
        del probe["pos_or_kw"]
        assert len(probe._dict) == 3
        del probe["var_pos"]
        assert len(probe._dict) == 2
        del probe["kw_only"]
        assert len(probe._dict) == 1
        del probe["var_kw"]
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
        assert "pos_only" in probe
        assert "not_a_param" not in probe

    def test__len__(self, probe):
        assert len(probe) == 5

    def test__str__(self, probe, method_probe):
        assert str(probe) == "some_func(pos_only, /, pos_or_kw, *var_pos, kw_only, **var_kw)"
        assert str(method_probe) == "SomeClass().some_method(self, pos_only, /, pos_or_kw, *var_pos, kw_only, **var_kw)"


def test_mapping_to_kwargs():
    def func(a, b, c):
        return a + b + c

    mappingI = {"a": 1, "b": 2, "c": 3, "d": 4}
    mappingII = {"a": 1, "b": 2}

    assert mapping_to_kwargs(mappingI, func) == {"a": 1, "b": 2, "c": 3}
    assert mapping_to_kwargs(mappingII, func) == {"a": 1, "b": 2}