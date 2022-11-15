import sqlite3
import os
import json
from pathlib import Path
from contextlib import contextmanager

from .core.classes import Expense, Income, Category
from .core.utils import time_from_str


class Database:
    def __init__(self, path: str | Path) -> None:
        self.path = path

    @contextmanager
    def connection(self):
        conn = sqlite3.connect(self.path)
        try:
            yield conn.cursor()
        finally:
            conn.commit()
            conn.close()
    
    # create database schema 
    def create_schema(self) -> None:
        with self.connection() as cursor:
            cursor.execute(
                """
                CREATE TABLE categories (
                    name TEXT PRIMARY KEY,
                    aliases TEXT
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE expenses (
                    id INTEGER PRIMARY KEY,
                    amount REAL,
                    category_name TEXT,
                    description TEXT,
                    time DATE,
                    FOREIGN KEY (category_name) REFERENCES categories(name)
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE incomes (
                    id INTEGER PRIMARY KEY,
                    amount REAL,
                    description TEXT,
                    time DATE
                )
                """
            )

    def add_income(self, income: Income) -> None:
        with self.connection() as cursor:
            cursor.execute(
                """
                INSERT INTO incomes (amount, description, time)
                VALUES (:amount, :description, :time)
                """,
                income._asdict()
            )
    
    def add_expense(self, expense: Expense) -> None:
        with self.connection() as cursor:
            cursor.execute(
                """
                INSERT INTO expenses (amount, description, time, category_name)
                VALUES (:amount, :description, :time, :category)
                """,
                expense._asdict()
            )
    
    def delete_last_expense(self) -> Expense:
        with self.connection() as cursor:
            # get last expense for the response to user
            cursor.execute(
                """
                SELECT * FROM expenses
                WHERE id = (SELECT MAX(id) FROM expenses)
                """
            )
            
            # get rid of id
            result = list(cursor.fetchone())[1:]

            # convert empty description to None
            if result[2] == "":
                result[2] = None

            # turn string with time into datetime object    
            result[3] = time_from_str(result[3])

            # construct Expense object
            expense = Expense(*result)

            # delete from database
            cursor.execute(
                """
                DELETE FROM expenses
                WHERE id = (SELECT MAX(id) FROM expenses)
                """
            )

            return expense
    
    def get_categories(self) -> list[Category]:
        with self.connection() as cursor:
            cursor.execute(
                """
                SELECT * FROM categories
                """
            )
            data = cursor.fetchall()
            categories = [
                Category(row[0], row[1].split())
                for row in data
            ]
            return categories

    def add_category(self, category: Category) -> None:
        name = category.name
        aliases = " ".join(category.aliases)
        with self.connection() as cursor:
            cursor.execute(
                """
                INSERT INTO categories (name, aliases) VALUES (?, ?)
                """,
                (name, aliases)
            )
    
    def delete_category(self, name: str) -> None:
        with self.connection() as cursor:
            cursor.execute(
                """
                DELETE FROM categories WHERE name = ?
                """,
                (name,)
            )


class Model:
    def __init__(self, folder: str) -> None:
        self.folder = folder
        self._folder_path = Path(folder).resolve(strict=True)
        self._balance_path = self._folder_path / "balance.txt"
        self._db_path = self._folder_path / "database.db"
        self.db = Database(self._db_path)
    
    # create and initialize all data files if they don't exist yet
    def setup(self) -> None:
        # create folder, database and balance file
        if not self._folder_path.exists():
            os.mkdir(self._folder_path)

        # create balance file
        if not self._balance_path.exists():
            with open(self._balance_path, "w") as f:
                f.write("0")

        # create database
        if not self._db_path.exists():
            self.db.create_schema()
            self.db.add_category(Category("other", ["другое"]))

            # if there is a starter json file with category names and aliases
            categories_path = self._folder_path / "categories.json"
            if categories_path.exists():
                with open(categories_path, "r", encoding="utf8") as f:
                    categories: dict[str, list[str]] = json.load(f)
                    categories = [
                        Category(name, aliases)
                        for name, aliases in categories.items()
                    ]
                    for category in categories:
                        self.db.add_category(category)
    
    def get_balance(self) -> float:
        with open(self._balance_path, "r") as f:
            balance = float(f.read())
            return balance
    
    def set_balance(self, new: float) -> None:
        with open(self._balance_path, "w") as f:
            f.write(str(new))