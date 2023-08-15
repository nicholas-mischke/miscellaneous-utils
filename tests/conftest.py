import pytest

@pytest.fixture
def some_func():
    def some_func(pos_only, /, pos_or_kw, *var_pos, kw_only, **var_kw):
        ...
    return some_func

@pytest.fixture
def some_method():
    class SomeClass:
        def some_method(self, pos_only, /, pos_or_kw, *var_pos, kw_only, **var_kw):
            ...
    return SomeClass().some_method