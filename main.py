import json
import sys

from potential import Potential
from suport import validate_values

ERROR_CODE = -1


def error_check(
        srcs: list[int], prps: list[int], tbl: list[list[int]]
):
    if len(error_codes := validate_values(srcs, prps, tbl)) > 0:
        error_str = ""
        if -1 in error_codes:
            error_str += "\nКоличество источников не совпадает с количеством строк платёжной" \
                         " матрицы!"
        if -2 in error_codes:
            error_str += "\nКоличество целей не совпадает с длинной одной или нескольких строк" \
                         " платёжной матрицы!"
        raise ValueError(error_str)


if __name__ == '__main__':
    sources: list[int]
    purposes: list[int]
    table: list[list[int]]
    try:
        with open("input.json", "r") as json_file:
            input_dict = json.load(json_file)
            table = input_dict["F"]
            sources = input_dict["A"]
            purposes = input_dict["B"]
        error_check(sources, purposes, table)
    except FileNotFoundError as fnfe:
        print(f"Файл input.json не найден.\n{fnfe}")
        sys.exit(ERROR_CODE)

    pot = Potential(sources, purposes, table)
    pot.calculate_transport()
    print("POTENTIAL METHOD:\n" + "\n\n".join(map(str, pot.get_tables_history())))
    print(f"\nRESULT:\n{pot.get_result()}")
