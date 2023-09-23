import pytest
from miscellaneous_utilities.iterables import (
    arg_to_iter,
    chunk_iter,
    all_indicies,
    sort_list_by_key,
    flatten,
    sort_list_by_attr,
)


@pytest.mark.parametrize(
    "arg, expected",
    [
        (None, []),
        ({"key": "value"}, [{"key": "value"}]),
        ("hello", ["hello"]),
        ([1, 2, 3], [1, 2, 3]),  # already an iterable
        (42, [42]),
        ((), ()),  # empty tuple should be returned as is
    ],
)
def test_arg_to_iter(arg, expected):
    assert arg_to_iter(arg) == expected


def test_chunk_iter():
    some_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    assert chunk_iter(some_list, 2) == ([1, 2], [3, 4], [5, 6], [7, 8], [9, 10])
    assert chunk_iter(some_list, 3) == ([1, 2, 3], [4, 5, 6], [7, 8, 9], [10])


@pytest.mark.parametrize(
    "iterable, obj, expected",
    [
        ("hello world hello world", "world", (6, 18)),
        ([1, 2, 3, 4, 1, 5, 1], 1, (0, 4, 6)),
        ("apple", "p", (1, 2)),
    ],
)
def test_all_indicies(iterable, obj, expected):
    assert all_indicies(iterable, obj) == expected


def test_all_indices_errors():
    with pytest.raises(AttributeError):
        all_indicies(42, 42)

    with pytest.raises(ValueError):
        all_indicies("hello", "z")


@pytest.mark.parametrize(
    "lst, key, reverse, expected",
    [
        (
            [
                {"name": "Alice", "age": 30},
                {"name": "Bob", "age": 25},
                {"name": "Charlie", "age": 35},
            ],
            "age",
            False,
            [
                {"name": "Bob", "age": 25},
                {"name": "Alice", "age": 30},
                {"name": "Charlie", "age": 35},
            ],
        ),
        (
            [
                {"name": "Alice", "age": 30},
                {"name": "Bob", "age": 25},
                {"name": "Charlie", "age": 35},
            ],
            "age",
            True,
            [
                {"name": "Charlie", "age": 35},
                {"name": "Alice", "age": 30},
                {"name": "Bob", "age": 25},
            ],
        ),
        (
            [
                {"product": "apple", "price": 1.2},
                {"product": "banana", "price": 0.8},
                {"product": "cherry", "price": 2.5},
            ],
            "price",
            False,
            [
                {"product": "banana", "price": 0.8},
                {"product": "apple", "price": 1.2},
                {"product": "cherry", "price": 2.5},
            ],
        ),
    ],
)
def test_sort_list_by_key(lst, key, reverse, expected):
    assert sort_list_by_key(lst, key, reverse) == expected


@pytest.mark.parametrize(
    "nested_list, expected",
    [
        ([], []),  # Empty list
        ([1, 2, 3], [1, 2, 3]),  # Already flat
        ([[1, 2], [3, 4]], [1, 2, 3, 4]),  # Two-level nesting
        ([1, [2, [3, 4]]], [1, 2, 3, 4]),  # Multi-level nesting
    ],
)
def test_flatten(nested_list, expected):
    assert list(flatten(nested_list)) == expected


def test_sort_list_by_attr():
    class Person:
        def __init__(self, name: str, age: int):
            self.name = name
            self.age = age

    people = [Person("Alice", 30), Person("Bob", 25), Person("Charlie", 35)]
    sorted_people = sort_list_by_attr(people, "age")

    assert [p.age for p in sorted_people] == [25, 30, 35]
