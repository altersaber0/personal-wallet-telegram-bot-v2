import unittest
from datetime import datetime
from bot.core.parser import parse_expense, parse_income, parse_month, parse_new_balance, command_type
from bot.core.classes import Command, Expense, Income
from bot.core.utils import time_now


class TestParser(unittest.TestCase):

    def test_expense_parsing(self):
        correct = ["-250 taxi",
                   "- 250 taxi",
                   "- 250 transport taxi"]
        incorrect = ["-sdf sdf",
                     "-250",
                     "-",
                     "- dfjgj"]

        for msg in incorrect:
            self.assertRaises(ValueError, parse_expense, msg)
        
        self.assertEqual(parse_expense(correct[0]), Expense(250, "other", "taxi", time_now()))
        self.assertEqual(parse_expense(correct[1]), Expense(250, "other", "taxi", time_now()))
        self.assertEqual(parse_expense(correct[2]), Expense(250, "transport", "taxi", time_now()))
    
    def test_income_parsing(self):
        correct = ["+250 from friend",
                   "+ 250 from friend",
                   "+ 250 found",
                   "+ 100.5 found"]
        incorrect = ["+250",
                     "+ 250",
                     "+hsfh",
                     "+ skdfkdsfk",
                     "+ sdf sfkskf dfs"]

        for msg in incorrect:
            self.assertRaises(ValueError, parse_income, msg)
        
        self.assertEqual(parse_income(correct[0]), Income(250, "from friend", time_now()))
        self.assertEqual(parse_income(correct[1]), Income(250, "from friend", time_now()))
        self.assertEqual(parse_income(correct[2]), Income(250, "found", time_now()))
        self.assertEqual(parse_income(correct[3]), Income(100.5, "found", time_now()))
    
    def test_new_balance_parsing(self):
        correct = ["balance 2000.567", "balance 2000", "bl 123.456", "bl 1000"]
        incorrect = ["balance ahdahd", "bl sdjfs", "bl 123dfsfd", "balance 123...89"]

        for msg in incorrect:
            self.assertRaises(ValueError, parse_new_balance, msg)
        
        self.assertEqual(parse_new_balance(correct[0]), 2000.567)
        self.assertEqual(parse_new_balance(correct[1]), 2000)
        self.assertEqual(parse_new_balance(correct[2]), 123.456)
        self.assertEqual(parse_new_balance(correct[3]), 1000)

    def test_month_parsing(self):
        curr = datetime.now()
        self.assertEqual(parse_month("month"), datetime(curr.year, curr.month, 1))
        self.assertEqual(parse_month("july"), datetime(curr.year, 7, 1))
        self.assertEqual(parse_month("july 2020"), datetime(2020, 7, 1))
    
    def test_command_type_recognition(self):
        self.assertEqual(command_type("-250 taxi"), Command.EXPENSE)
        self.assertEqual(command_type("- 250 taxi"), Command.EXPENSE)
        self.assertEqual(command_type("+250 from friend"), Command.INCOME)
        self.assertEqual(command_type("+ 250 from friend"), Command.INCOME)
        self.assertEqual(command_type("balance"), Command.BALANCE)
        self.assertEqual(command_type("bl"), Command.BALANCE)
        self.assertEqual(command_type("balance 2000"), Command.BALANCE_NEW)
        self.assertEqual(command_type("balance dksf"), Command.BALANCE_NEW)
        self.assertEqual(command_type("cancel"), Command.CANCEL)
        self.assertEqual(command_type("month"), Command.MONTH)
        self.assertEqual(command_type("july"), Command.MONTH)
        self.assertEqual(command_type("july 2020"), Command.MONTH)
        self.assertEqual(command_type("dsfds"), Command.UNKNOWN)
        self.assertEqual(command_type("balanc"), Command.UNKNOWN)
        self.assertEqual(command_type("augusts"), Command.UNKNOWN)
        self.assertEqual(command_type("july sfdhf"), Command.UNKNOWN)