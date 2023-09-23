import re


# trunk-ignore(ruff/D417)
def normalize_space(string: str) -> str:
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

    # Remove leading and trailing whitespaces
    return string.strip()


def normalize_newlines(
    string: str, leading_newline: bool = False, trailing_newline: bool = True
) -> str:
    """
    Turns 2+ newlines into 2 newlines, leaving single blankline.
    Removes leading and trailing whitespace. Adds leading and trailing newlines if specified.

    Typically used when writing to a text file.

    Examples:
    --------
    >>> normalize_newlines("hello\\n\\n\\nworld", False, True)
    'hello\\n\\nworld\\n'

    """
    string = re.sub(r"\n{2,}", "\n\n", string).strip()  # 2+ blanklines to one blankline

    if leading_newline:
        string = "\n" + string
    if trailing_newline:
        string += "\n"

    return string
