from functools import reduce


def __is_eq_len_list_listlist__(arr: list[float], arr2d: list[list[float]]):
    return reduce(
        lambda b1, b2: b1 and b2,
        map(lambda row: len(row) == len(arr), arr2d)
    )


def validate_values(
        sources: list[int], purposes: list[int], table: list[list[int]]
) -> bool:
    error_codes = set()
    if len(sources) != len(table):
        error_codes.add(-1)
    if not __is_eq_len_list_listlist__(purposes, table):
        error_codes.add(-2)
    return error_codes
