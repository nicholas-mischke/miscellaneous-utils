import pytest
from utils.strings import normalize_space


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
