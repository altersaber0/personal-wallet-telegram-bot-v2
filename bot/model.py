import sqlite3
import os
from pathlib import Path

class Model:
    def __init__(self, folder_path: Path) -> None:
        self.folder_path = folder_path.resolve()
        self.balance_path = self.folder_path / "balance.txt"
        self.db_path = self.folder_path / "database.db"
    
    def setup(self) -> None:
        if not self.folder_path.exists():
            os.mkdir(self.folder_path)
            with open(self.balance_path, "w") as f:
                f.write("0")
    
    def get_balance(self) -> float:
        with open(self.balance_path, "r") as f:
            balance = float(f.read())
            return balance
    
    def set_balance(self, new: float) -> None:
        with open(self.balance_path, "w") as f:
            f.write(str(new))
