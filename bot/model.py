import sqlite3
import os
from pathlib import Path

class Model:
    def __init__(self, folder_path: Path) -> None:
        self.folder_path = folder_path.resolve()
        self._balance_path = self.folder_path / "balance.txt"
        self._db_path = self.folder_path / "database.db"
    
    def setup(self) -> None:
        if not self.folder_path.exists():
            os.mkdir(self.folder_path)
            with open(self._balance_path, "w") as f:
                f.write("0")

        if not self._balance_path.exists():
            with open(self._balance_path, "w") as f:
                f.write("0")
        
        if not self._db_path.exists():
            pass
    
    def get_balance(self) -> float:
        with open(self._balance_path, "r") as f:
            balance = float(f.read())
            return balance
    
    def set_balance(self, new: float) -> None:
        with open(self._balance_path, "w") as f:
            f.write(str(new))
