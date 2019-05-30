#!/usr/bin/env python
from functools import reduce


def is_valid_hp(hp: str) -> bool:
    assert isinstance(
        hp, str
    ), "The input type for a hp (hierarchy path) must be a string."
    # assert hp[0] == "/", "A hp (hierarchy path) should start with '/' at a root."
    return True


# hp tools
def is_int(maybe_i) -> bool:
    "Predicate for if input is able to be casted to an integer."
    try:
        int(maybe_i)
        return True
    except ValueError:
        return False


def maybe_int(thing) -> bool:
    "If a valid int cast the type, else return our input."
    if is_int(thing):
        return int(thing)
    else:
        return thing


def list_to_hp(li: list) -> str:
    """
    Converts a list (used for toolz get_in, assoc_in, update_in) to a hp
    (hierarchy path).

    Input: ['root', 0, 'thing',2]
    Output:   /root/0/thing/2
    """
    assert isinstance(li, list), "The input type for li must be a list."
    assert "/" not in li, "Can't have our path delimiter in our list?"
    return "/" + "/".join([str(x) for x in li])


def hp_to_list(hp: str) -> list:
    """Converts a hp (hieriarchy path) to a list (lists are used for toolz's
    get_in, assoc_in, updated_in, etc.).

    Input: /root/0/thing/2
    Output: ['root', 0, 'thing',2]

    """
    # assert hp[0] == '/', "Hierarchy path must start with a '/' (from root)?"
    is_valid_hp(hp)
    li = [maybe_int(p) for p in hp.split("/") if p != ""]
    return li


def is_wildcard_hp(hp: str) -> bool:
    "Predicate for If path string has a wildcard char someplace in it's path."
    # assert hp[0] == '/', "Hierarchy path must start with a '/' (from root)?"
    is_valid_hp(hp)
    if "/*/" in hp:
        return True
    else:
        return False


def flatten_recur(recursive_lists: list) -> list:
    "Utility function to flatten many nested recursive lists."
    assert isinstance(recursive_lists, list)
    if recursive_lists == []:  # done
        return recursive_lists

    first, *rest = recursive_lists

    if isinstance(first, list):
        return flatten_recur(first) + flatten_recur(rest)
    else:
        return [first] + flatten_recur(rest)


def get_in_hp(hp: str, d: dict, default=None, no_default=False):
    """Toolz's `get_in` function takes a tuple and a dict, and returns the value
    at that place in the dict.

    get_in_hp does basically the same thing, but rather than a tuple takes a
    "hierarchy path" (hp) string.

    The enhancement here is a Hierarchy Path can have wildcards, denoted by a *,
    for a globbing like effect.

    See test_get_in_hp_usage() for usage examples.
    """
    is_valid_hp(hp)
    if not is_wildcard_hp(hp):  # easy
        path_list = hp_to_list(hp)
        try:
            return reduce(lambda x, y: x.__getitem__(y), path_list, d)
        except (KeyError, IndexError, TypeError):
            if no_default:
                raise
            return default
    else:
        parent_path, rest_path = hp.split("/*/", 1)
        child_data = get_in_hp(parent_path, d)
        assert isinstance(
            child_data, (list, type(None))
        ), "Wildcard's need lists as children?"

        if child_data:
            return [get_in_hp(rest_path, x) for x in child_data]


def assoc_in_coll(d: dict, coll: list, value, factory=dict) -> dict:
    "Same idea as assoc_in, however uses `coll` similarly to toolz.get_in()."
    assert (
        len(coll) >= 1
    ), "we should have at least one collection key to get and one collection key to set."

    d2 = factory()
    d2.update(d)

    *getters, setter = coll
    # this mutates d2
    # TODO Will raise a KeyError if path doesn't exist. Do i want that?
    reduce(lambda x, y: x.__getitem__(y), getters, d2).__setitem__(setter, value)
    return d2


def assoc_in_hp(d: dict, hp: str, value, factory=dict) -> dict:
    "Wrapper around assoc_in_coll() to use a hierarchy path."
    is_valid_hp(hp)

    coll = hp_to_list(hp)
    return assoc_in_coll(d, coll, value, factory)


def explode_path(hp: str, d: dict, parent=None):
    is_valid_hp(hp)
    if not is_wildcard_hp(hp):
        # if it's not a wildcard hp, actually we can just return 'it' (there is only one.)
        return [hp]
    else:
        parent_path, rest_path = hp.split("/*/", 1)
        child_data = get_in_hp(parent_path, d)
        assert isinstance(
            child_data, (list, type(None))
        ), "Wildcard's need lists as children?"
        if child_data:
            return [
                explode_path("/".join([parent_path, str(i), rest_path]), d)
                for i, _ in enumerate(child_data)
            ]


def update_in_hp(d, hp, func, default=None, factory=dict):
    is_valid_hp(hp)

    def __update_in_hp(d, hp):
        v = func(get_in_hp(hp, d, default=default))
        return assoc_in_hp(d, hp, v, factory=factory)

    if not is_wildcard_hp(hp):
        return __update_in_hp(d, hp)
    else:
        # get all the hierarchy paths we are working with, remove None's, and
        # flatten:
        hps = [x for x in flatten_recur(explode_path(hp, d)) if x]
        # reduce across the paths on the input dict.
        r = reduce(__update_in_hp, hps, d)
        return r
