from pathlib import Path
import inspect
import json
import sys
from typing import Any, Union
from functools import partial


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

# noqa
def reprint(*args, **kwargs):
    """
    Reprint by deleting the last line and printing the given arguments.

    The function uses ANSI escape codes:
    - "\033[1A": Moves the cursor up one line.
    - "\x1b[2K": Clears the current line.

    Args:
        *args: Variable length argument list to be printed.
        **kwargs: Arbitrary keyword arguments passed to the print function.
    """
    # Move the cursor up one line
    print("\033[1A", end="")

    # Clear the current line
    print("\x1b[2K", end="")

    # Print the given arguments
    print(*args, **kwargs)
