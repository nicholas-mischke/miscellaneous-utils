import pytest
from misc_utils import (
    normalize_space,
    normalize_newlines,
    CaseConverter,
)


@pytest.mark.parametrize(
    "input_string, expected",
    [
        ("hello   world", "hello world"),
        ("   leading and trailing spaces   ", "leading and trailing spaces"),
        ("multiple   spaces   between   words", "multiple spaces between words"),
        ("line\nbreaks", "line breaks"),
        ("tabs\tshould\talso\tbe\tspaces", "tabs should also be spaces"),
        ("\u200bZero\u200bWidth\ufeffSpaces", "ZeroWidthSpaces"),
    ],
)
def test_normalize_space(input_string, expected):
    assert normalize_space(input_string) == expected


@pytest.mark.parametrize(
    "input_string, leading_newline, trailing_newline, expected",
    [
        (
            "\n\n\nmultiple\n\n\n\n\nspaces\n\n\nbetween\n\n\nwords\n\n\n",
            False,
            False,
            "multiple\n\nspaces\n\nbetween\n\nwords",
        ),
        (
            "\n\n\nmultiple\n\n\n\n\nspaces\n\n\nbetween\n\n\nwords\n\n\n",
            True,
            False,
            "\nmultiple\n\nspaces\n\nbetween\n\nwords",
        ),
        (
            "\n\n\nmultiple\n\n\n\n\nspaces\n\n\nbetween\n\n\nwords\n\n\n",
            False,
            True,
            "multiple\n\nspaces\n\nbetween\n\nwords\n",
        ),
    ],
)
def test_normalize_newlines(
    input_string: str, leading_newline: bool, trailing_newline: bool, expected: str
):
    assert (
        normalize_newlines(input_string, leading_newline, trailing_newline) == expected
    )


@pytest.mark.parametrize(
    "input_string",
    [
        "hello_world",
        "HelloWorld",
        "helloWorld",
        "hello-world",
    ],
)
def test_case_converter(input_string):
    converter = CaseConverter(input_string)
    assert converter.snake_case == "hello_world"
    assert converter.pascal_case == "HelloWorld"
    assert converter.camel_case == "helloWorld"
    assert converter.kebab_case == "hello-world"


def test_case_converter_class_names():
    converter = CaseConverter("ThisIsANameOfAClass")
    assert converter.snake_case == "this_is_a_name_of_a_class"
    assert converter.pascal_case == "ThisIsANameOfAClass"
    assert converter.camel_case == "thisIsANameOfAClass"
    assert converter.kebab_case == "this-is-a-name-of-a-class"
    assert converter.word_list == [
        "this",
        "is",
        "a",
        "name",
        "of",
        "a",
        "class",
    ]

def test_case_converter_error():
    with pytest.raises(ValueError):
        CaseConverter("")

    with pytest.raises(ValueError):
        CaseConverter("Hello, Wolrd!")


if __name__ == "__main__":
    from pathlib import Path
    from pprint import pprint
    import pytest

    test_file = Path(__file__).absolute()
    test_class_or_function = None
    test_method = None

    # test_class_or_function = ''
    # test_method = ''

    test_path = test_file
    if test_class_or_function is not None:
        test_path = f"test_path::{test_class_or_function}"
    if test_method is not None:
        test_path = f"test_path::{test_method}"

    args = [
        test_path,
        "-s",
        "--verbose",
    ]

    pytest.main(args)
