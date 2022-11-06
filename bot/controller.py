from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.update import Update

from .core.classes import Expense, Income, Command
from .core.parser import command_type, parse_expense, parse_income, parse_month, parse_new_balance
from .view import View
from .model import Model

class Controller:
    def __init__(self, telegram_api_key: str, telegram_user_id: int, view: View, model: Model) -> None:
        self.updater = Updater(token=telegram_api_key)
        self.user_filter = Filters.user(user_id=telegram_user_id)
        self.view = view
        self.model = model
    
    # /start command
    def start(self, update: Update, context) -> None:
        self.view.reply(update, "Bot started.")
    
    # /help command
    def help(self, update: Update, context) -> None:
        self.view.reply(update, "\n".join([
        "Text commands:",
        "add expense: \"- amount (category | description)\"",
        "add income: \"+ amount description\"",
        "check balance: \"(balance | bl)\"",
        "change balance: \"(balance | bl) amount\"",
        "month statistics: \"(month | {concrete}) (year)\"",
        "cancel last expense: \"cancel\"",
        "",
        "Slash commands:",
        "/start - start the bot",
        "/help - this message",
        "/expense - add expense",
        "/income - add income",
        "/balance - check balance",
        "/month - current month statistics",
        "/cancel - cancel last expense",
        "/categories - show category names",
        ]))
    
    # /balance command
    def balance(self, update: Update, context) -> None:
        balance = self.model.get_balance()
        self.view.reply_balance(update, balance)

    # /cancel command
    def cancel(self, update: Update, context) -> None:
        expense = self.model.delete_last_expense()
        self.view.reply_cancel(update, expense)

    # /categories command
    def categories(self, update: Update, context) -> None:
        response = f"Categories:\n"
        for idx, categories in enumerate(self.model.get_categories().items(), start=1):
            name = categories[0]
            aliases = categories[1]
            response += f"{idx}. {name.capitalize()}: {', '.join(aliases)}\n"
        self.view.reply(update, response)
    
    # match text message type to corresponding reply or error
    def handle_message(self, update: Update, context) -> None:
        message = update.message.text
        command = command_type(message)
        try:
            match command:
                case Command.EXPENSE:
                    categories = self.model.get_categories()
                    expense = parse_expense(message, categories)
                    self.model.add_expense(expense)
                    # update balance accordingly
                    balance = self.model.get_balance()
                    self.model.set_balance(balance - expense.amount)
                    self.view.reply_expense(update, expense)
                case Command.INCOME:
                    income = parse_income(message)
                    self.model.add_income(income)
                    # update balance accordingly
                    balance = self.model.get_balance()
                    self.model.set_balance(balance + income.amount)
                    self.view.reply_income(update, income)
                case Command.CANCEL:
                    expense = self.model.delete_last_expense()
                    self.view.reply_cancel(update, expense)
                case Command.BALANCE:
                    balance = self.model.get_balance()
                    self.view.reply_balance(update, balance)
                case Command.BALANCE_NEW:
                    new = parse_new_balance(message)
                    self.model.set_balance(new)
                    self.view.reply_balance(update, new)
                case Command.UNKNOWN:
                    self.view.reply(update, "Unknown text command.")
                    
        except ValueError:
            self.view.reply_error(update, command)
    
    def start_bot(self, poll_interval: float, timeout: float) -> None:
        # create DB and balance files if they don't exist yet
        self.model.setup()

        # add /command and message handlers
        dp = self.updater.dispatcher
        dp.add_handler(CommandHandler("start", self.start, filters=self.user_filter))
        dp.add_handler(CommandHandler("help", self.help, filters=self.user_filter))
        dp.add_handler(CommandHandler("categories", self.categories, filters=self.user_filter))
        dp.add_handler(CommandHandler("balance", self.balance, filters=self.user_filter))
        dp.add_handler(CommandHandler("cancel", self.cancel, filters=self.user_filter))

        # filter out /command messages
        dp.add_handler(MessageHandler(Filters.text & (~Filters.command) & self.user_filter, self.handle_message))
        
        # start polling updates from Telegram servers
        print("Bot running...")
        self.updater.start_polling(poll_interval=poll_interval, timeout=timeout)
        self.updater.idle()