import pytest

from misc_utils import json_dump, json_load, rmdir_non_empty, reprint, ordinal


def test_json_functions(tmp_path):
    """Test json_dump and json_load functions."""
    # Using pytest's tmp_path fixture to create a temporary file for testing
    data = {"key": "value"}
    file_path = tmp_path / "test.json"

    json_dump(data, file_path)
    loaded_data = json_load(file_path)

    assert data == loaded_data

def test_rmdir_non_empty(tmpdir):
    """Test rmdir_non_empty function."""

    dirpath = tmpdir.mkdir("test")
    filepath = dirpath / "test.txt"

    filepath.write("hello world")

    rmdir_non_empty(dirpath)

    assert not dirpath.exists()

@pytest.mark.parametrize(
    "n, expected",
    [
        (1, "1st"),
        (2, "2nd"),
        (3, "3rd"),
        (4, "4th"),
        (5, "5th"),
        (6, "6th"),
        (7, "7th"),
        (8, "8th"),
        (9, "9th"),
        (10, "10th"),
        (11, "11th"),
        (12, "12th"),
        (13, "13th"),
    ],
)
def test_ordinal(n, expected):
    assert ordinal(n) == expected


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
