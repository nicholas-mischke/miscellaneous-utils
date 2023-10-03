"""
Pytest or Python (Haven't dug deep enough to know which) has a funny way of dealing
with nested functions, or functions used in parametrization / fixtures.

some_func and many_params can be seen as methods if used in this way, so we
declare them here in a normal python file, so not to introduce bugs to the test suite.
"""


def some_func(a, b, c):
    ...


def many_params(
    pos_only_param, /, pos_or_kw_param, *var_pos_param, kw_only_param, **var_kw_param
):
    ...


class SomeClass:
    def __init__(self, a, b, c):
        ...

    def some_method(self, some_param):
        ...

    def many_params(
        self,
        pos_only_param,
        /,
        pos_or_kw_param,
        *var_pos_param,
        kw_only_param,
        **var_kw_param,
    ):
        ...


some_instance = SomeClass(1, 2, 3)

def with_a_default(a, b, c=3):
    ...


if __name__ == "__main__":
    import inspect

    print(str(inspect.signature(some_func)))

    print(str(inspect.signature(SomeClass.many_params)))
    print(str(inspect.signature(some_instance.many_params)))

    print(f"{inspect.ismethod(SomeClass.many_params)}")
    print(f"{inspect.ismethod(some_instance.many_params)}")
