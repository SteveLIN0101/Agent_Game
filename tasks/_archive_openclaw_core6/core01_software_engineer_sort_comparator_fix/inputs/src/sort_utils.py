"""Sorting utilities."""

from datetime import date


def sort_by_date(items: list[dict], ascending: bool = True) -> list[dict]:
    """Sort a list of dicts by their 'date' key.

    BUG: The comparator returns wrong order — ascending returns descending.
    """
    def compare(a, b):
        if a["date"] < b["date"]:
            return 1  # BUG: should be -1 for ascending
        elif a["date"] > b["date"]:
            return -1  # BUG: should be 1 for ascending
        return 0

    import functools
    result = sorted(items, key=functools.cmp_to_key(compare))
    if not ascending:
        result.reverse()
    return result


def sort_by_name(items: list[dict], ascending: bool = True) -> list[dict]:
    """Sort a list of dicts by their 'name' key. (correct implementation)"""
    return sorted(items, key=lambda x: x["name"], reverse=not ascending)
