from pathlib import Path
import inspect
import json
import sys
from typing import Any, Union
from functools import partial


# trunk-ignore(ruff/D417)
def json_dump(data: Any, path: Union[str, Path]) -> None:
    """Dump data to a JSON file.

    Args:
    ----
        data (Any): The data to be serialized.
        path (Union[str, Path]): The path to the file to which the data will be written.

    Returns:
    -------
        None
    """
    with Path(path).open("w") as f:
        json.dump(data, f)


# trunk-ignore(ruff/D417)
def json_load(path: Union[str, Path]) -> Any:
    """Load data from a JSON file.

    Args:
    ----
        path (Union[str, Path]): The path to the file from which the data will be read.

    Returns:
    -------
        Any: The deserialized data.
    """
    with Path(path).open("r") as f:
        return json.load(f)


