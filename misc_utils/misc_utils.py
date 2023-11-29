from pathlib import Path
import json
from typing import Any, Union

try:
    from .decorator_utils import export
except ImportError:
    from decorator_utils import export


@export
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


@export
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


@export
def rmdir_non_empty(dirpath: Union[str, Path], missing_ok: bool = False):
    """Remove a directory and all its contents.

    Args:
    ----
        dirpath (Union[str, Path]): The path to the directory to be removed.

    Returns:
    -------
        None
    """
    dirpath = Path(dirpath)

    if not dirpath.is_dir():
        if missing_ok:
            return
        raise NotADirectoryError(f"{dirpath} is not a directory.")

    # Must first remove all files, before we can remove any directories.
    files = set(f for f in dirpath.rglob("*") if f.is_file())

    for f in files:
        f.unlink()

    dirs = list(f for f in dirpath.rglob("*") if f.is_dir())
    dirs.sort(reverse=True)  # Remove deepest directories first

    for d in dirs:
        d.rmdir()
    dirpath.rmdir()


# noqa
@export
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


@export
def ordinal(n: int) -> str:
    """
    Convert an integer into its ordinal representation.

    Adds an ordinal suffix ('st', 'nd', 'rd', or 'th') to an integer, making it
    an ordinal number as a string. For example, 1 becomes '1st', 2 becomes '2nd',
    3 becomes '3rd', and 4 becomes '4th'.

    Parameters:
        n (int): The integer to convert.

    Returns:
        str: The integer with its ordinal suffix.
    """
    # Define the suffixes for ordinal numbers
    suffix = ["th", "st", "nd", "rd", "th"][min(n % 10, 4)]

    # Special cases for numbers between 11 and 13
    if 11 <= (n % 100) <= 13:
        suffix = "th"

    return str(n) + suffix
