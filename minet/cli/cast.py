from typing import cast

class CSVRowCaster(object):
    def __init__(self, rules, headers) -> None:
        self.rules = rules
        self.headers = headers

    def cast_row(self, row, fieldnames = None):
        if not fieldnames: fieldnames = self.headers
        return [self.try_cast(fieldnames[i], row[i]) for i in range(len(row))]

    def try_cast(self, field, value):
        dt = self.rules.get(field)
        if not dt or not value: return value
        if isinstance(value, dt): return value
        try:
            return dt(value)
        except Exception:
            return value

