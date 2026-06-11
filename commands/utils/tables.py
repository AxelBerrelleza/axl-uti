from typing import Any, Callable, Dict, List, Tuple, Union
from rich.table import Table

ColumnSpec = Union[str, Tuple[str, str], Tuple[str, str, Callable[[Any], str] | None]]


class Tables:
    @staticmethod
    def from_dict(
        data: Dict[str, Any],
        *,
        value_formatter: Callable[[Any], str] | None = str,
    ) -> Table:
        table = Table(*data.keys())
        values = (
            value_formatter(val) if value_formatter and val is not None else ""
            for val in data.values()
        )
        table.add_row(*values)
        return table

    @staticmethod
    def from_list(
        data: List[Dict[str, Any]],
        columns: List[ColumnSpec],
    ) -> Table:
        headers: List[str] = []
        key_mappings: List[str] = []
        formatters: List[Callable[[Any], str] | None] = []

        for col in columns:
            if isinstance(col, str):
                headers.append(col)
                key_mappings.append(col)
                formatters.append(str)
            elif len(col) == 2:
                headers.append(col[0])
                key_mappings.append(col[1])
                formatters.append(str)
            else:
                headers.append(col[0])
                key_mappings.append(col[1])
                formatters.append(col[2])

        table = Table(*headers)
        for row in data:
            cells = []
            for key, fmt in zip(key_mappings, formatters):
                val = row.get(key)
                if val is not None and fmt is not None:
                    cells.append(fmt(val))
                else:
                    cells.append("")
            table.add_row(*cells)
        return table
