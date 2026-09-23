import os
import sqlite3
from contextlib import closing


class Database:
    """
    SQLite database layer for Student Bot.

    Handles:
    - database connection
    - students CRUD operations
    - advertising history
    - statistics
    - Telegram ID retrieval
    """

    def __init__(
        self,
        path_to_db: str = "data/students.db",
    ) -> None:
        self.path_to_db = path_to_db

        directory = os.path.dirname(
            self.path_to_db
        )

        if directory:
            os.makedirs(
                directory,
                exist_ok=True,
            )

        self.create_table_students()
        self.create_table_advertisements()

    # ============================================================
    # CONNECTION
    # ============================================================

    def _connect(self) -> sqlite3.Connection:
        """
        Create and configure a new SQLite connection.
        """

        connection = sqlite3.connect(
            self.path_to_db,
            timeout=10,
        )

        connection.row_factory = sqlite3.Row

        return connection

    # ============================================================
    # STUDENTS TABLE
    # ============================================================

    def create_table_students(self) -> None:
        """
        Create students table if it does not exist.
        """

        query = """
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                age INTEGER NOT NULL,
                phone TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """

        with closing(
            self._connect()
        ) as connection:

            try:
                connection.execute(query)
                connection.commit()

            except sqlite3.Error:
                connection.rollback()
                raise

    # ============================================================
    # ADVERTISEMENTS TABLE
    # ============================================================

    def create_table_advertisements(self) -> None:
        """
        Create advertising history table if it does not exist.
        """

        query = """
            CREATE TABLE IF NOT EXISTS advertisements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_id INTEGER NOT NULL,
                message_text TEXT NOT NULL,
                total_users INTEGER NOT NULL DEFAULT 0,
                successful_sends INTEGER NOT NULL DEFAULT 0,
                failed_sends INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """

        with closing(
            self._connect()
        ) as connection:

            try:
                connection.execute(query)
                connection.commit()

            except sqlite3.Error:
                connection.rollback()
                raise

    # ============================================================
    # STUDENTS
    # ============================================================

    def add_student(
        self,
        telegram_id: int,
        first_name: str,
        last_name: str,
        age: int,
        phone: str,
    ) -> None:
        """
        Add a new student.
        """

        query = """
            INSERT INTO students (
                telegram_id,
                first_name,
                last_name,
                age,
                phone
            )
            VALUES (?, ?, ?, ?, ?)
        """

        parameters = (
            telegram_id,
            first_name,
            last_name,
            age,
            phone,
        )

        with closing(
            self._connect()
        ) as connection:

            try:
                connection.execute(
                    query,
                    parameters,
                )

                connection.commit()

            except sqlite3.Error:
                connection.rollback()
                raise

    def get_student(
        self,
        telegram_id: int,
    ) -> sqlite3.Row | None:
        """
        Get one student by Telegram ID.
        """

        query = """
            SELECT
                id,
                telegram_id,
                first_name,
                last_name,
                age,
                phone,
                created_at
            FROM students
            WHERE telegram_id = ?
            LIMIT 1
        """

        with closing(
            self._connect()
        ) as connection:

            cursor = connection.execute(
                query,
                (telegram_id,),
            )

            return cursor.fetchone()

    def get_all_students(
        self,
    ) -> list[sqlite3.Row]:
        """
        Get all students ordered by newest
        registration first.
        """

        query = """
            SELECT
                id,
                telegram_id,
                first_name,
                last_name,
                age,
                phone,
                created_at
            FROM students
            ORDER BY id DESC
        """

        with closing(
            self._connect()
        ) as connection:

            cursor = connection.execute(
                query
            )

            return cursor.fetchall()

    def get_all_telegram_ids(self) -> list[int]:
        """
        Get Telegram IDs of all registered students.
        """

        query = """
            SELECT telegram_id
            FROM students
            ORDER BY id ASC
        """

        with closing(
            self._connect()
        ) as connection:

            cursor = connection.execute(
                query
            )

            return [
                row["telegram_id"]
                for row in cursor.fetchall()
            ]

    def count_students(self) -> int:
        """
        Return the total number of registered students.
        """

        query = """
            SELECT COUNT(*)
            FROM students
        """

        with closing(
            self._connect()
        ) as connection:

            cursor = connection.execute(
                query
            )

            result = cursor.fetchone()

            return int(result[0])

    def update_student(
        self,
        telegram_id: int,
        first_name: str,
        last_name: str,
        age: int,
        phone: str,
    ) -> bool:
        """
        Update student data.

        Returns:
            True if a student was updated.
            False if the student was not found.
        """

        query = """
            UPDATE students
            SET
                first_name = ?,
                last_name = ?,
                age = ?,
                phone = ?
            WHERE telegram_id = ?
        """

        parameters = (
            first_name,
            last_name,
            age,
            phone,
            telegram_id,
        )

        with closing(
            self._connect()
        ) as connection:

            try:
                cursor = connection.execute(
                    query,
                    parameters,
                )

                connection.commit()

                return cursor.rowcount > 0

            except sqlite3.Error:
                connection.rollback()
                raise

    def delete_student(
        self,
        telegram_id: int,
    ) -> bool:
        """
        Delete a student by Telegram ID.
        """

        return self.delete_student_by_telegram_id(
            telegram_id
        )

    def delete_student_by_telegram_id(
        self,
        telegram_id: int,
    ) -> bool:
        """
        Delete a student by Telegram ID.

        Returns:
            True if deleted.
            False if not found.
        """

        query = """
            DELETE FROM students
            WHERE telegram_id = ?
        """

        with closing(
            self._connect()
        ) as connection:

            try:
                cursor = connection.execute(
                    query,
                    (telegram_id,),
                )

                connection.commit()

                return cursor.rowcount > 0

            except sqlite3.Error:
                connection.rollback()
                raise

    # ============================================================
    # ADVERTISEMENTS
    # ============================================================

    def add_advertisement(
        self,
        admin_id: int,
        message_text: str,
        total_users: int,
        successful_sends: int,
        failed_sends: int,
    ) -> int:
        """
        Save a completed advertisement.

        Returns:
            ID of the created advertisement.
        """

        query = """
            INSERT INTO advertisements (
                admin_id,
                message_text,
                total_users,
                successful_sends,
                failed_sends
            )
            VALUES (?, ?, ?, ?, ?)
        """

        parameters = (
            admin_id,
            message_text,
            total_users,
            successful_sends,
            failed_sends,
        )

        with closing(
            self._connect()
        ) as connection:

            try:
                cursor = connection.execute(
                    query,
                    parameters,
                )

                connection.commit()

                return int(cursor.lastrowid)

            except sqlite3.Error:
                connection.rollback()
                raise

    def get_last_advertisement(
        self,
    ) -> sqlite3.Row | None:
        """
        Get the latest advertisement.
        """

        query = """
            SELECT
                id,
                admin_id,
                message_text,
                total_users,
                successful_sends,
                failed_sends,
                created_at
            FROM advertisements
            ORDER BY id DESC
            LIMIT 1
        """

        with closing(
            self._connect()
        ) as connection:

            cursor = connection.execute(
                query
            )

            return cursor.fetchone()

    def get_advertisement_history(
        self,
        limit: int = 20,
    ) -> list[sqlite3.Row]:
        """
        Get advertisement history.

        Args:
            limit: Maximum number of records.
        """

        query = """
            SELECT
                id,
                admin_id,
                message_text,
                total_users,
                successful_sends,
                failed_sends,
                created_at
            FROM advertisements
            ORDER BY id DESC
            LIMIT ?
        """

        with closing(
            self._connect()
        ) as connection:

            cursor = connection.execute(
                query,
                (limit,),
            )

            return cursor.fetchall()

    def count_advertisements(self) -> int:
        """
        Return the total number of advertisements.
        """

        query = """
            SELECT COUNT(*)
            FROM advertisements
        """

        with closing(
            self._connect()
        ) as connection:

            cursor = connection.execute(
                query
            )

            result = cursor.fetchone()

            return int(result[0])