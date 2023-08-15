import re


# trunk-ignore(ruff/D417)
def normalize_space(string: str) -> str:
    # trunk-ignore(ruff/D301)
    """
    Assumes utf-8 encoding.

    Turn all whitespaces into a single space (b'\x20').
    Leave no leading or trailing whitespace.

    Args:
    ----
        string (str): The input string to be normalized.

    Returns:
    -------
        str: The normalized string.
    """

    # Remove zero-width spaces
    string = re.sub(r"[\u200b\ufeff]", "", string)

    # Combine any number of whitespaces into a single space
    string = re.sub(r"\s+", " ", string)

    return string.strip()


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
