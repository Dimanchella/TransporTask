import copy
from itertools import product


class PaymentTable:
    sources: list
    purposes: list
    table: list[list]
    name: str

    def __init__(
            self, sources: list[int], purposes: list[int],
            table: list[list[int]], name: str
    ):
        self.sources = copy.copy(sources)
        self.purposes = copy.copy(purposes)
        self.table = copy.deepcopy(table)
        self.name = name

    def __str__(self):
        chars = [[self.name] + list(map(
            lambda el: str(el) if el is not None else '-', self.purposes
        ))]
        for i in range(len(self.sources)):
            chars.append(list(map(
                lambda el: str(el) if el is not None else '-',
                [self.sources[i]] + self.table[i]
            )))
        max_char_len = max(list(map(
            lambda cs_row: max(list(map(len, cs_row))),
            chars
        )))
        for i, j in product(range(len(chars)), range(len(chars[0]))):
            chars[i][j] = ' ' * (max_char_len - len(chars[i][j])) + chars[i][j]
        return "\n".join(list(map(' '.join, chars)))

    def __copy__(self):
        return PaymentTable(
            copy.copy(self.sources),
            copy.copy(self.purposes),
            copy.deepcopy(self.table),
            self.name
        )

    def adding_table(self):
        if (ss := sum(filter(
                lambda el: type(el) == int, self.sources
        ))) != (ps := sum(filter(
                lambda el: type(el) == int, self.purposes
        ))):
            if ss < ps:
                self.sources.append(ps - ss)
                self.table.append([0] * len(self.purposes))
            if ss > ps:
                self.purposes.append(ss - ps)
                for row in self.table:
                    row.append(0)
