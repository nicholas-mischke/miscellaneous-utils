from operator import itemgetter
from typing import Iterable, List, Tuple, Union, Any, Dict


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

    Returns:
    -------
        Iterable: The converted iterable.
    """

    # Combining the varargs and the default values into one tuple
    iter_single_values = default_iter_single_values + tuple(
        additional_iter_single_values
    )

    if arg is None:
        return []
    elif not isinstance(arg, iter_single_values) and hasattr(arg, "__iter__"):
        return arg
    else:
        return [arg]


def chunk_iter(iterable, chunk_size):
    """
    Split an iterable into successive chunks using index subscriptions.

    Args:
        iterable (iterable): An iterable to split into chunks.
        chunk_size (int): The size of each chunk.

    Returns:
        tuple: A tuple containing chunks of the iterable.
    """
    return tuple(
        iterable[pos : pos + chunk_size] for pos in range(0, len(iterable), chunk_size)
    )


def all_indicies(iterable: Union[str, Iterable], obj: Any) -> Tuple[int]:
    """Find all indices of an object in an iterable.

    Args:
    ----
        iterable (Union[str, Iterable]): The iterable to search in.
        obj (Any): The object to search for.

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
