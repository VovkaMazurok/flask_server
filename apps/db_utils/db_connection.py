import logging
import sqlite3
import types

from apps.settings import DB_PATH


class DBConnection:
    """
    A context manager for managing SQLite database connections.
    """
    def __init__(self) -> None:
        try:
            # Establish a connection to the SQLite database
            self.connection: sqlite3.Connection = sqlite3.connect(DB_PATH)
            # Configure the connection to return rows as dictionaries
            self.connection.row_factory = sqlite3.Row  # Return rows as dictionaries
        except sqlite3.Error as e:
            # Log an error if the connection fails
            logging.exception(f"Failed to connect to the database: {e}")
            raise

    def __enter__(self) -> sqlite3.Connection:
        # Return the database connection when entering the context
        return self.connection

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> bool | None:
        # Log any exception that occurs within the context
        if exc_type:
            logging.error(f"An error occurred: {exc_val}")
        try:
            # Commit changes if no exception occurred
            if exc_type is None:
                self.connection.commit()
        finally:
            # Ensure the connection is closed
            self.connection.close()
        return None
