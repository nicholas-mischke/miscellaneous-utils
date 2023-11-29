from operator import itemgetter
from typing import Iterable, List, Tuple, Union, Any, Dict

try:
    from .decorator_utils import export
except ImportError:
    from decorator_utils import export


@export
def arg_to_iter(
    arg: Union[None, Iterable, Any],
    *additional_iter_single_values: Iterable,
    default_iter_single_values: Tuple = (bytes, dict, str)
) -> Iterable:
    """Convert an argument to an iterable.

    Args:
    ----
        arg (Union[None, Iterable, Any]): The argument to be converted.
            Can be None, a single value, or an iterable.
        *additional_iter_single_values (Iterable): Additional types to be considered as single values.
        default_iter_single_values (Iterable, optional): Default types to be considered as single values.
            Defaults to (bytes, dict, str).

    Examples:
    --------
    >>> arg_to_iter(None)
    []

    >>> arg_to_iter("hello")
    ['hello']

    >>> arg_to_iter([1, 2, 3])
    [1, 2, 3]

    >>> arg_to_iter(42)
    [42]

    Returns:
    -------
        Iterable: The converted iterable.
    """

    # Combining the varargs and the default values into one tuple
    iter_single_values = default_iter_single_values + additional_iter_single_values

    if arg is None:
        return []
    elif not isinstance(arg, iter_single_values) and hasattr(arg, "__iter__"):
        return arg
    else:
        return [arg]


@export
def chunk_iter(iterable, chunk_size):
    """
    Split an iterable into successive chunks using index subscriptions.

    Args:
    ----
        iterable (iterable): An iterable to split into chunks.
        chunk_size (int): The size of each chunk.

    Examples:
    --------
    >>> chunk_iter([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 2)
    ([1, 2], [3, 4], [5, 6], [7, 8], [9, 10])

    Returns:
    -------
        tuple: A tuple containing chunks of the iterable.
    """
    return tuple(
        iterable[pos : pos + chunk_size] for pos in range(0, len(iterable), chunk_size)
    )


@export
def flatten(sequence: Union[Iterable, Any]) -> List:
    """Flatten a sequence into a single, flat list.

    Returns a single, flat list which contains all elements retrieved
    from the sequence and all recursively contained sub-sequences (iterables).

    Examples:
    --------
    >>> flatten([1, 2, [3, 4], (5, 6)])
    [1, 2, 3, 4, 5, 6]
    >>> flatten([[[1, 2, 3], (42, None)], [4, 5], [6], 7, (8, 9, 10)])
    [1, 2, 3, 42, None, 4, 5, 6, 7, 8, 9, 10]
    >>> flatten(["foo", "bar"])
    ['foo', 'bar']
    >>> flatten(["foo", ["baz", 42], "bar"])
    ['foo', 'baz', 42, 'bar']
    """
    result = []

    # Recursive helper function to flatten a sequence
    def _flatten(seq: Union[Iterable, Any]):
        nonlocal result
        for el in seq:
            if hasattr(el, "__iter__") and not isinstance(el, (str, bytes)):
                _flatten(el)
            else:
                result.append(el)

    _flatten(sequence)
    return result


@export
def all_indicies(iterable: Union[str, Iterable], obj: Any) -> Tuple[int]:
    """Find all indices of an object in an iterable.

    Args:
    ----
        iterable (Union[str, Iterable]): The iterable to search in.
        obj (Any): The object to search for.

    Examples:
    --------
    >>> all_indicies("hello world hello world", "world")
    (6, 18)

    >>> all_indicies([1, 2, 3, 4, 1, 5, 1], 1)
    (0, 4, 6)

    Returns:
    -------
        Tuple[int]: A tuple containing all the indices of the object in the iterable.

    Raises:
    ------
        AttributeError: If the iterable does not have an __iter__ attribute.
        ValueError: If the object is not found in the iterable.
    """
    if not hasattr(iterable, "__iter__"):
        raise AttributeError()

    indices, split = [], 0
    while split < len(iterable):
        try:
            indices.append(iterable[split:].index(obj) + split)
            split = indices[-1] + 1
        except ValueError:  # obj not in this chunk of the iterable
            break

    if not indices:
        raise ValueError()
    return tuple(indices)

    # indicies = []
    # for i, item in enumerate(iterable):
    #     if item == obj:
    #         indices.append(i)
    # if not indices:
    #     raise ValueError()
    # return tuple(indices)


@export
def sort_list_by_key(lst: List[Dict], key: str, reverse: bool = False) -> List[Dict]:
    """Sort a list of mappings based on the values of a specific key.

    Args:
    ----
        lst (List[Dict]): The list of mappings to be sorted.
        key (str): The key based on which the list will be sorted.
        reverse (bool, optional): If True, sort the list in descending order. Defaults to False.

    Returns:
    -------
        List[Dict]: The sorted list.
    """
    return sorted(lst, key=itemgetter(key), reverse=reverse)


@export
def sort_list_by_attr(lst: List[Any], attr: str, reverse: bool = False) -> List[Any]:
    """Sort a list of objects based on the values of a specific attribute.

    Args:
    ----
        lst (List[Any]): The list of objects to be sorted.
        attr (str): The attribute based on which the list will be sorted.
        reverse (bool, optional): If True, sort the list in descending order. Defaults to False.

    Returns:
    -------
        List[Any]: The sorted list.
    """
    return sorted(lst, key=lambda x: getattr(x, attr), reverse=reverse)
