import sqlite3
from typing import List, Tuple, Any
from datetime import datetime

class DatabaseHelper:
    def __init__(self):
        """
        Initialize DatabaseHelper with the database file name.
        """
        self.db_name = "novel_data.db"
        self._initialize_database()

    def _connect(self):
        """
        Create a connection to the SQLite database.

        :return: SQLite connection object.
        """
        return sqlite3.connect(self.db_name)

    def _initialize_database(self):
        """
        Initialize the database with the required table.
        """
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS novels (
                    novel_id INTEGER PRIMARY KEY,
                    latest_chapter_id INTEGER NOT NULL,
                    novel_name TEXT,
                    latest_update_time TEXT NOT NULL
                )
            """)

    def _create_chapter_table(self, novel_id):
        """
        Create a chapter table for a specific novel ID.

        :param novel_id: The ID of the novel for which to create the chapter table.
        """
        table_name = f"novel_{novel_id}"
        with self._connect() as conn:
            conn.execute(f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    chapter_id INTEGER PRIMARY KEY,
                    title TEXT,
                    content TEXT
                )
            """)

    def _current_time(self) -> str:
        """
        Get the current time in the format YYYY-MM-DD-HH-MM.

        :return: The formatted current time as a string.
        """
        return datetime.now().strftime("%Y-%m-%d-%H-%M")

    def add_chapter(self, novel_id: int, chapter_id: int, title: str, content: str) -> None:
        """
        Add a chapter to the chapter table of the specified novel.

        :param novel_id: The ID of the novel to which the chapter belongs.
        :param chapter_id: The ID of the chapter.
        :param title: The title of the chapter.
        :param content: The content of the chapter.
        """
        self._create_chapter_table(novel_id)
        table_name = f"novel_{novel_id}"
        with self._connect() as conn:
            conn.execute(f"""
                INSERT INTO {table_name} (chapter_id, title, content)
                VALUES (?, ?, ?)
            """, (chapter_id, title, content))

        # Update the novel's latest chapter ID and time
        self.update_novel(novel_id, chapter_id, self._current_time())

    def add_novel(self, novel_id: int, latest_chapter_id: int) -> None:
        """
        Add a new novel to the novels table and create a new table named after the novel_id.

        :param novel_id: The ID of the novel.
        :param latest_chapter_id: The latest chapter ID of the novel.
        :param state: The state of the novel (e.g., ongoing, completed).
        """
        with self._connect() as conn:
            conn.execute("""
                INSERT INTO novels (novel_id, latest_chapter_id, latest_update_time)
                VALUES (?, ?, ?)
            """, (novel_id, latest_chapter_id, self._current_time()))
            self._create_chapter_table(novel_id)

    def name_novel(self, nocel_id, novel_name):
        with self._connect() as conn:
            conn.execute("""
                UPDATE novels
                SET novel_name =  ?
                WHERE novel_id = ?
            """, (novel_name))

    def update_novel(self, novel_id: int, latest_chapter_id: int, latest_update_time: str) -> None:
        """
        Update an existing novel in the novels table. If the novel_id does not exist, insert it.

        :param novel_id: The ID of the novel.
        :param latest_chapter_id: The latest chapter ID of the novel.
        :param latest_update_time: The latest update time of the novel in the format YYYY-MM-DD-HH-MM.
        """
        with self._connect() as conn:
            # Check if the novel_id exists
            novel_exists = conn.execute("""
                SELECT 1
                FROM novels
                WHERE novel_id = ?
            """, (novel_id,)).fetchone()

            if novel_exists:
                # Update the existing record
                conn.execute("""
                    UPDATE novels
                    SET latest_chapter_id = ?, latest_update_time = ?
                    WHERE novel_id = ?
                """, (latest_chapter_id, latest_update_time, novel_id))
            else:
                # Insert a new record
                conn.execute("""
                    INSERT INTO novels (novel_id, latest_chapter_id, latest_update_time)
                    VALUES (?, ?, ?)
                """, (novel_id, latest_chapter_id, latest_update_time))


    def get_novel_by_id(self, novel_id: int) -> Any:
        """
        Retrieve a novel by its ID.

        :param novel_id: The ID of the novel.
        :return: The novel record or None if not found.
        """
        with self._connect() as conn:
            return conn.execute("""
                SELECT * FROM novels WHERE novel_id = ?
            """, (novel_id,)).fetchone()

    def get_all_novels(self) -> List[Tuple]:
        """
        Retrieve all novels from the novels table.

        :return: A list of all novel records.
        """
        with self._connect() as conn:
            return conn.execute("""
                SELECT * FROM novels
            """).fetchall()

    def delete_novel(self, novel_id: int) -> None:
        """
        Delete a novel by its ID and drop the corresponding table.

        :param novel_id: The ID of the novel to delete.
        """
        with self._connect() as conn:
            conn.execute("""
                DELETE FROM novels WHERE novel_id = ?
            """, (novel_id,))
            conn.execute(f"""
                DROP TABLE IF EXISTS novel_{novel_id}
            """)

# Example usage
if __name__ == "__main__":
    db_helper = DatabaseHelper()

