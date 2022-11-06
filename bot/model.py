import sqlite3
import os
import json
from pathlib import Path

from .core.classes import Expense, Income

def create_database(path: Path) -> None:
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE categories (name TEXT PRIMARY KEY)""")
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

    conn.commit()
    conn.close()

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
            with open(self._balance_path, "w") as f:
                f.write("0")

        # create balance file
        if not self._balance_path.exists():
            with open(self._balance_path, "w") as f:
                f.write("0")

        # create database
        if not self._db_path.exists():
            create_database(self._db_path)
    
    def get_balance(self) -> float:
        with open(self._balance_path, "r") as f:
            balance = float(f.read())
            return balance
    
    def set_balance(self, new: float) -> None:
        with open(self._balance_path, "w") as f:
            f.write(str(new))
    
    def get_categories(self) -> dict[str, list[str]]:
        with open(self._categories_path, "r", encoding="utf8") as f:
            categories_dict = json.loads(f.read())
        return categories_dict