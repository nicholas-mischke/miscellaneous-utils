import pytest
from miscellaneous_utilities.strings import normalize_space, normalize_newlines


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
        ("\n\n\nmultiple\n\n\n\n\nspaces\n\n\nbetween\n\n\nwords\n\n\n", False, False, "multiple\n\nspaces\n\nbetween\n\nwords"),
        ("\n\n\nmultiple\n\n\n\n\nspaces\n\n\nbetween\n\n\nwords\n\n\n", True, False, "\nmultiple\n\nspaces\n\nbetween\n\nwords"),
        ("\n\n\nmultiple\n\n\n\n\nspaces\n\n\nbetween\n\n\nwords\n\n\n", False, True, "multiple\n\nspaces\n\nbetween\n\nwords\n"),
    ]
)
def test_normalize_newlines(input_string: str, leading_newline: bool, trailing_newline: bool, expected: str):
    assert normalize_newlines(input_string, leading_newline, trailing_newline) == expected

if __name__ == "__main__":
    pytest.main(["-k", "test_normalize"])