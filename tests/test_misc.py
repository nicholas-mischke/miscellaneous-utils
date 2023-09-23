import pytest

from miscellaneous_utilities.misc import json_dump, json_load


def test_json_functions(tmp_path):
    """Test json_dump and json_load functions."""
    # Using pytest's tmp_path fixture to create a temporary file for testing
    data = {"key": "value"}
    file_path = tmp_path / "test.json"

    json_dump(data, file_path)
    loaded_data = json_load(file_path)

    assert data == loaded_data


