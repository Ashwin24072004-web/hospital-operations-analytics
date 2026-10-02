from collections.abc import Mapping, Sequence
from typing import Any

import pandas as pd
import psycopg
from psycopg.rows import dict_row

from src.config import database_url


def fetch_all(sql: str, params: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    """Execute a read-only query and return rows as dictionaries."""
    with psycopg.connect(database_url(), row_factory=dict_row) as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, params or {})
            return list(cursor.fetchall())


def fetch_value(sql: str, params: Mapping[str, Any] | None = None) -> Any:
    rows = fetch_all(sql, params)
    if not rows:
        return None
    return next(iter(rows[0].values()))


def fetch_dataframe(sql: str, params: Mapping[str, Any] | None = None) -> pd.DataFrame:
    return pd.DataFrame(fetch_all(sql, params))


def execute_many(sql: str, rows: Sequence[Sequence[Any]]) -> None:
    """Utility reserved for local data-loading scripts, not the dashboard."""
    with psycopg.connect(database_url()) as connection:
        with connection.cursor() as cursor:
            cursor.executemany(sql, rows)

