import unittest
from datetime import datetime

from bot.core.interfaces import Expense, Income
from bot.core.utils import time_now
from bot.model import Database