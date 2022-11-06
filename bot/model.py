import sqlite3
import os
import json
from pathlib import Path
from contextlib import contextmanager

from .core.classes import Expense, Income


class Model:
    def __init__(self, folder: str) -> None:
        self.folder = folder
        self._folder_path = Path(folder).resolve(strict=True)
        self._balance_path = self._folder_path / "balance.txt"
        self._db_path = self._folder_path / "database.db"
        self._categories_path = self._folder_path / "categories.json"
    
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
            self.create_database()
    
    def get_balance(self) -> float:
        with open(self._balance_path, "r") as f:
            balance = float(f.read())
            return balance
    
    def set_balance(self, new: float) -> None:
        with open(self._balance_path, "w") as f:
            f.write(str(new))
    
    def get_categories(self) -> dict[str, list[str]]:
        with open(self._categories_path, "r", encoding="utf8") as f:
            categories = json.loads(f.read())
        return categories
    
    @contextmanager
    def db_connection(self):
        conn = sqlite3.connect(self._db_path)
        try:
            yield conn.cursor()
        finally:
            conn.commit()
            conn.close()
    
    def create_database(self):
        with self.db_connection() as cursor:
            cursor.execute(
                """
                CREATE TABLE categories (
                    name TEXT PRIMARY KEY
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE expenses (
                    amount REAL,
                    description TEXT,
                    time DATE PRIMARY KEY,
                    category_name TEXT,
                    FOREIGN KEY (category_name) REFERENCES categories(name)
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE incomes (
                    amount REAL,
                    description TEXT,
                    time DATE PRIMARY KEY
                )
                """
            )
    
    def add_expense(self, expense: Expense) -> None:
        ...

    def delete_last_expense(self) -> Expense:
        ...
    
    def add_income(self, income: Income) -> None:
        ...