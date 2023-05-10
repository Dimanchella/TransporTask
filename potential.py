import copy
from itertools import product
from functools import reduce

from tables import PaymentTable


class Potential:
    __payment_table__: PaymentTable
    __plan_history__: list[PaymentTable]
    __support_history__: list[PaymentTable]
    __delta_history__: list[PaymentTable]
    __t_history__: list[PaymentTable]

    def __init__(self, sources: list[int], purposes: list[int], table: list[list[int]]):
        self.__payment_table__ = PaymentTable(sources, purposes, table, "C")
        self.__payment_table__.adding_table()

    def get_tables_history(self):
        return copy.deepcopy([self.__payment_table__] + list(reduce(
            lambda h1, h2: h1 + h2, list(map(
                lambda plan, supp, delta, t: [plan, supp, delta, t],
                self.__plan_history__, self.__support_history__,
                self.__delta_history__, self.__t_history__
            ))
        ))) + [self.__plan_history__[-1], self.__support_history__[-1], self.__delta_history__[-1]]

    def get_result(self):
        return copy.deepcopy(
            self.__plan_history__[-1]
            if len(self.__plan_history__)
            else self.__payment_table__
        )

    def __find_negative_delta__(self):
        c_table = self.__payment_table__.table
        delta = self.__delta_history__[-1].table
        re_row, re_col = -1, -1
        min_delta = 1
        min_c = -1
        for i, j in product(range(len(delta)), range(len(delta[0]))):
            if min_delta > delta[i][j] < 0:
                min_delta = delta[i][j]
                min_c = c_table[i][j]
                re_row, re_col = i, j
            elif min_delta == delta[i][j] < 0 and min_c > c_table[i][j]:
                min_c = c_table[i][j]
                re_row, re_col = i, j
        return re_row, re_col

    def __create_first_plan__(self):
        plan_sources = copy.copy(self.__payment_table__.sources)
        plan_purposes = copy.copy(self.__payment_table__.purposes)
        plan_table = [[None] * len(plan_purposes) for _ in range(len(plan_sources))]
        i, j = 0, 0
        while i < len(plan_sources) and j < len(plan_purposes):
            if plan_sources[i] - plan_purposes[j] >= 0:
                plan_table[i][j] = plan_purposes[j]
                plan_sources[i] -= plan_purposes[j]
                plan_purposes[j] = 0
                j += 1
            else:
                plan_table[i][j] = plan_sources[i]
                plan_purposes[j] -= plan_sources[i]
                plan_sources[i] = 0
                i += 1
        self.__plan_history__.append(PaymentTable(
            self.__payment_table__.sources, self.__payment_table__.purposes,
            plan_table, "P1"
        ))

    def __create_supporting_table__(self):
        u_table = [0] + [None] * (len(self.__payment_table__.sources) - 1)
        v_table = [None] * len(self.__payment_table__.purposes)
        plan_table = self.__plan_history__[-1].table
        payment_table = self.__payment_table__.table
        uv_table = [
            [
                payment_table[i][j] if plan_table[i][j] is not None else None
                for j in range(len(v_table))
            ]
            for i in range(len(u_table))
        ]
        while None in u_table or None in v_table:
            for i, j in product(range(len(u_table)), range(len(v_table))):
                if uv_table[i][j] is not None:
                    if u_table[i] is not None and v_table[j] is None:
                        v_table[j] = uv_table[i][j] - u_table[i]
                    elif v_table[j] is not None and u_table[i] is None:
                        u_table[i] = uv_table[i][j] - v_table[j]
        for i, j in product(range(len(u_table)), range(len(v_table))):
            if uv_table[i][j] is None:
                uv_table[i][j] = u_table[i] + v_table[j]
        self.__support_history__.append(PaymentTable(
            u_table, v_table,
            uv_table, f"~C{len(self.__support_history__) + 1}"
        ))

    def __create_delta_table__(self):
        c_table = self.__payment_table__.table
        uv_table = self.__support_history__[-1].table
        delta = [
            [
                c_table[i][j] - uv_table[i][j]
                for j in range(len(c_table[i]))
            ]
            for i in range(len(c_table))
        ]
        self.__delta_history__.append(PaymentTable(
            [None] * len(c_table), [None] * len(c_table[0]),
            delta, f"D{len(self.__delta_history__) + 1}"
        ))

    def __find_t_row__(
            self, cur_row: int, cur_col: int, re_col: int,
            plan: list[list[int]], t_signs: list[list[int]]
    ):
        for i in range(len(plan)):
            if i != cur_row and plan[i][cur_col] is not None:
                t_signs[i][cur_col] = 1
                next_t_signs = self.__find_t_col__(i, cur_col, re_col, plan, t_signs)
                if next_t_signs != -1:
                    return next_t_signs
                t_signs[i][cur_col] = 0
        return -1

    def __find_t_col__(
            self, cur_row: int, cur_col: int, re_col: int,
            plan: list[list[int]], t_signs: list[list[int]]
    ):
        for j in range(len(plan[0])):
            if j != cur_col and plan[cur_row][j] is not None:
                t_signs[cur_row][j] = -1
                if j == re_col:
                    return t_signs
                next_t_signs = self.__find_t_row__(cur_row, j, re_col, plan, t_signs)
                if next_t_signs != -1:
                    return next_t_signs
                t_signs[cur_row][j] = 0
        return -1

    def __create_t_table__(self, re_row, re_col):
        last_plan = copy.deepcopy(self.__plan_history__[-1].table)
        t_table = [[0] * len(last_plan[0]) for _ in range(len(last_plan))]
        t_table[re_row][re_col] = 1
        t_table = self.__find_t_col__(re_row, re_col, re_col, last_plan, t_table)
        self.__t_history__.append(PaymentTable(
            [None] * len(self.__payment_table__.sources),
            [None] * len(self.__payment_table__.sources),
            t_table, f"T{len(self.__t_history__) + 1}"
        ))

    def __create_next_plan__(self, re_row, re_col):
        new_plan_table = copy.deepcopy(self.__plan_history__[-1].table)
        t_table = self.__t_history__[-1].table
        min_t, max_c = -1, -1
        new_plan_table[re_row][re_col] = 0
        for i, j in product(range(len(new_plan_table)), range(len(new_plan_table[0]))):
            if t_table[i][j] == -1:
                if new_plan_table[i][j] < min_t or min_t < 0:
                    max_c = self.__payment_table__.table[i][j]
                    min_t = new_plan_table[i][j]
                    re_row, re_col = i, j
                elif new_plan_table[i][j] == min_t and self.__payment_table__.table[i][j] > max_c:
                    max_c = self.__payment_table__.table[i][j]
                    min_t = new_plan_table[i][j]
                    re_row, re_col = i, j
        new_plan_table[re_row][re_col] = None
        for i, j in product(range(len(new_plan_table)), range(len(new_plan_table[0]))):
            if new_plan_table[i][j] is not None:
                new_plan_table[i][j] += min_t * t_table[i][j]
        self.__plan_history__.append(PaymentTable(
            self.__payment_table__.sources, self.__payment_table__.purposes,
            new_plan_table, f"P{len(self.__plan_history__) + 1}"
        ))

    def calculate_transport(self):
        self.__plan_history__ = []
        self.__support_history__ = []
        self.__delta_history__ = []
        self.__t_history__ = []
        self.__create_first_plan__()
        self.__create_supporting_table__()
        self.__create_delta_table__()
        while (re_coord := self.__find_negative_delta__())[0] >= 0:
            self.__create_t_table__(*re_coord)
            self.__create_next_plan__(*re_coord)
            self.__create_supporting_table__()
            self.__create_delta_table__()
