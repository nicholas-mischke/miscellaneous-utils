import re
from typing import Optional, Dict


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


class CaseConverter:
    """
    Class for converting strings between different cases.

    Attributes:
    - input_string (str): The original string input.
    """

    def __init__(self, input_string: str):
        """
        Initialize the CaseConverter with the original string.

        Parameters:
        - input_string (str): The original string to be formatted.

        Raises:
        - ValueError: If the original string does not match any supported case.
        """
        self.input_string = input_string

        if not self.input_string:
            raise ValueError("The input string is empty.")
        elif self.is_snake_case(input_string):  # variable and function names
            self.case = "snake"
        elif self.is_pascal_case(input_string):  # class names
            self.case = "pascal"
        elif self.is_camel_case(
            input_string
        ):  # some languages use camelCase for variables and functions
            self.case = "camel"
        elif self.is_kebab_case(
            input_string
        ):  # some languages use kebab-case for variables and functions
            self.case = "kebab"
        else:
            raise ValueError("The input string does not match any supported case.")

    @staticmethod
    def is_snake_case(string: str) -> bool:
        """
        Returns `True` if the string is in snake_case, `False` otherwise.

        Accepts only lowercase, alphanumeric characters seperated by underscores.

        Conventionally, in Python, variables and functions are snake_case.

        Examples:
        --------
        >>> # Accepts one or more words
        >>> CaseConverter.is_snake_case("hello_world")
        True
        >>> CaseConverter.is_snake_case("hello")
        True
        ...
        >>> CaseConverter.is_snake_case("HelloWorld") # PascalCase
        False
        >>> CaseConverter.is_snake_case("helloWorld") # camelCase
        False
        >>> CaseConverter.is_snake_case("hello-world") # kebab-case
        False
        ...
        >>> CaseConverter.is_snake_case("Hello, World!") # invalid characters
        False
        """

        # Matches any character that is not a lowercase letter, a number, or an underscore.
        # Removes any matching characters, and checks for equality.
        return string == re.sub(r"[^a-z0-9_]", "", string)

    @staticmethod
    def is_pascal_case(string: str) -> bool:
        """
        Returns `True` if the string is in PascalCase, `False` otherwise.

        Accepts only alphanumeric characters, starting with an uppercase letter.

        Conventionally, in Python, classes are PascalCase.

        Examples:
        --------
        >>> # Accepts one or more words
        >>> CaseConverter.is_pascal_case("HelloWorld")
        True
        >>> CaseConverter.is_pascal_case("Hello")
        True
        ...
        >>> CaseConverter.is_pascal_case("helloWorld") # camelCase
        False
        >>> CaseConverter.is_pascal_case("hello_world") # snake_case
        False
        >>> CaseConverter.is_pascal_case("hello-world") # kebab-case
        False
        ...
        >>> CaseConverter.is_pascal_case("Hello, World!") # invalid characters
        False
        """
        if (
            string.isalnum() is False  # Only alphanumeric characters
            or string[0].isupper() is False  # starts with an uppercase letter
            or string.lower() == string  # Considered snake_case
            or string.upper() == string  # Considered a CONSTANT in Python convention
        ):
            return False
        return True

    @staticmethod
    def is_camel_case(string: str) -> bool:
        """
        Returns `True` if the string is in camelCase, `False` otherwise.

        Examples:
        --------
        >>> # Accepts two or more words
        >>> CaseConverter.is_camel_case("helloWorld")
        True
        >>> CaseConverter.is_camel_case("hello") # snake_case
        False
        ...
        >>> CaseConverter.is_camel_case("HelloWorld") # PascalCase
        False
        >>> CaseConverter.is_camel_case("hello_world") # snake_case
        False
        >>> CaseConverter.is_camel_case("hello-world") # kebab-case
        False
        ...
        >>> CaseConverter.is_camel_case("Hello, World!") # invalid characters
        False
        """
        if (
            string.isalnum() is False  # Only alphanumeric characters
            or string[0].islower() is False  # starts with a lowercase letter
            or string.lower() == string  # Considered snake_case
            or string.upper() == string  # Considered a CONSTANT in Python convention
        ):
            return False
        return True

    @staticmethod
    def is_kebab_case(string: str) -> bool:
        """
        Returns `True` if the string is in kebab-case, `False` otherwise.

        Accepts only lowercase, alphanumeric characters seperated by hypens.
        If the string doesn't contain any hypens, it is considered snake_case.

        Examples:
        --------
        >>> # Accepts two or more words
        >>> CaseConverter.is_kebab_case("hello-world")
        True
        >>> CaseConverter.is_kebab_case("hello") # snake_case
        False
        ...
        >>> CaseConverter.is_kebab_case("HelloWorld") # PascalCase
        False
        >>> CaseConverter.is_kebab_case("helloWorld") # camelCase
        False
        >>> CaseConverter.is_kebab_case("hello_world") # snake_case
        False
        ...
        >>> CaseConverter.is_kebab_case("Hello, World!") # invalid characters
        False
        """
        # Matches any character that is not a lowercase letter, a number, or a hypen.
        # Removes any matching characters, and checks for equality.
        return string == re.sub(r"[^a-z0-9-]", "", string) and "-" in string

    @property
    def word_list(self) -> list[str]:
        """
        Split the string into a list of lower-case words.

        Examples:
        --------
        >>> CaseConverter("hello_world").word_list # snake_case
        ['hello', 'world']
        >>> CaseConverter("HelloWorld").word_list # PascalCase
        ['hello', 'world']
        >>> CaseConverter("helloWorld").word_list # camelCase
        ['hello', 'world']
        >>> CaseConverter("hello-world").word_list # kebab-case
        ['hello', 'world']

        Returns:
        ------
        - list[str]: The list of lower-case words.
        """

        if self.case == "snake":
            words = self.input_string.split("_")
        elif self.case == "pascal":
            words = re.findall(r"[A-Z][a-z]*", self.input_string)
        elif self.case == "camel":
            words = re.findall(r"[a-z]+|[A-Z][a-z]*", self.input_string)
        elif self.case == "kebab":
            words = self.input_string.split("-")

        return [word.lower() for word in words]

    # ... snake_case properties ...
    @property
    def snake_case(self) -> str:
        """
        Converts the string to snake_case.

        Examples:
        --------
        >>> CaseConverter("hello_world").snake_case # snake_case
        'hello_world'
        >>> CaseConverter("HelloWorld").snake_case # PascalCase
        'hello_world'
        >>> CaseConverter("helloWorld").snake_case # camelCase
        'hello_world'
        >>> CaseConverter("hello-world").snake_case # kebab-case
        'hello_world'
        """
        return "_".join(self.word_list)

    @property
    def pascal_case(self) -> str:
        """
        Converts the string to PascalCase.

        Examples:
        --------
        >>> CaseConverter("hello_world").pascal_case # snake_case
        'HelloWorld'
        >>> CaseConverter("HelloWorld").pascal_case # PascalCase
        'HelloWorld'
        >>> CaseConverter("helloWorld").pascal_case # camelCase
        'HelloWorld'
        >>> CaseConverter("hello-world").pascal_case # kebab-case
        'HelloWorld'
        """
        return "".join(word.title() for word in self.word_list)

    @property
    def PascalCase(self) -> str:
        """
        Converts the string to PascalCase.

        Examples:
        --------
        >>> CaseConverter("hello_world").pascal_case # snake_case
        'HelloWorld'
        >>> CaseConverter("HelloWorld").pascal_case # PascalCase
        'HelloWorld'
        >>> CaseConverter("helloWorld").pascal_case # camelCase
        'HelloWorld'
        >>> CaseConverter("hello-world").pascal_case # kebab-case
        'HelloWorld'
        """
        return self.pascal_case

    @property
    def camel_case(self) -> str:
        """
        Converts the input string to camelCase.

        Examples:
        --------
        >>> CaseConverter("hello_world").camel_case # snake_case
        'helloWorld'
        >>> CaseConverter("HelloWorld").camel_case # PascalCase
        'helloWorld'
        >>> CaseConverter("helloWorld").camel_case # camelCase
        'helloWorld'
        >>> CaseConverter("hello-world").camel_case # kebab-case
        'helloWorld'
        """
        return self.word_list[0] + "".join(word.title() for word in self.word_list[1:])

    @property
    def camelCase(self) -> str:
        """
        Converts the input string to camelCase.

        Examples:
        --------
        >>> CaseConverter("hello_world").camel_case # snake_case
        'helloWorld'
        >>> CaseConverter("HelloWorld").camel_case # PascalCase
        'helloWorld'
        >>> CaseConverter("helloWorld").camel_case # camelCase
        'helloWorld'
        >>> CaseConverter("hello-world").camel_case # kebab-case
        'helloWorld'
        """
        return self.camel_case

    @property
    def kebab_case(self) -> str:
        """
        Converts the input string to kebab-case.

        Example:
        -------
        >>> StringFormatter("hello_world").kebab_case # snake_case
        'hello-world'
        >>> StringFormatter("HelloWorld").kebab_case # PascalCase
        'hello-world'
        >>> StringFormatter("helloWorld").kebab_case # camelCase
        'hello-world'
        >>> StringFormatter("hello-world").kebab_case # kebab-case
        'hello-world'
        """
        return "-".join(self.word_list)


if __name__ == "__main__":
    print(CaseConverter("").snake_case)

    # doctest.testmod()

    # print("Hello World".isalnum())
