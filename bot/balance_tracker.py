import time
from datetime import datetime

from .model import Model


def track_balance(model: Model) -> None:
    """Store current balance into DB at the end of every month (1 minute before the end)."""

    while True:
        # Get how much time to wait in seconds
        current = datetime.now()

        # get next month datetime obj
        if current.month < 12:
            next_month = datetime(current.year, current.month + 1, 1)
        else:
            next_month = datetime(current.year + 1, 1, 1)

        # calculate difference in seconds - 60
        # (so the datetime.now() clearly stays in bounds of the current month)
        waiting_time = (next_month - current).total_seconds() - 60
        
        time.sleep(waiting_time)
        
        # store current balance into DB
        now = datetime.now().replace(microsecond=0)
        balance = model.get_balance()
        model.db.add_balance_to_history(now, balance)

        # sleep additional 60 seconds so the next iteration clearly deals with next coming month
        time.sleep(120)