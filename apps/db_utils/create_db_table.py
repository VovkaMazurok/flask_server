from apps.db_utils.db_connection import DBConnection


def create_db_table() -> None:
    """Create an SQLite table for users."""
    with (
        DBConnection() as connection,
        connection,
    ):
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL
            )
            """,
        )
