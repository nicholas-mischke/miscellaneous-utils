import pytest


@pytest.fixture
def some_func():
    def some_func(
        pos_only_param,
        /,
        pos_or_kw_param,
        *var_pos_param,
        kw_only_param,
        **var_kw_param,
    ):
        ...

    return some_func


@pytest.fixture
def some_constructor():
    class SomeClass:
        def __init__(
            self,
            pos_only_param,
            /,
            pos_or_kw_param,
            *var_pos_param,
            kw_only_param,
            **var_kw_param,
        ):
            ...

    return SomeClass


@pytest.fixture
def some_method():
    class SomeClass:
        def some_method(
            self,
            pos_only_param,
            /,
            pos_or_kw_param,
            *var_pos_param,
            kw_only_param,
            **var_kw_param,
        ):
            ...

    return SomeClass().some_method


@pytest.fixture
def some_callable_class():
    class SomeClass:
        def __call__(
            self,
            pos_only_param,
            /,
            pos_or_kw_param,
            *var_pos_param,
            kw_only_param,
            **var_kw_param,
        ):
            ...

    return SomeClass()
