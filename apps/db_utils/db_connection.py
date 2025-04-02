import sqlite3
import types

from apps.settings import DB_PATH


class DBConnection:
    def __init__(self) -> None:
        self.connection: sqlite3.Connection = sqlite3.connect(DB_PATH)
        self.connection.row_factory = sqlite3.Row  # Note: return rows as dictionaries

    def __enter__(self) -> sqlite3.Connection:
        return self.connection

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> bool | None:
        self.connection.close()
        return None
