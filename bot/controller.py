from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Filters
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
        "set balance: \"'balance' amount\"",
        "month statistics: \"(month | {concrete}) (year)\"",
        "",
        "Slash commands:",
        "/start - start the bot",
        "/help - this message",
        "/expense - add expense (conversation)",
        "/income - add income (conversation)",
        "/balance - check balance",
        "/month - current month statistics",
        "/cancel_last - cancel last expense",
        "/categories - show category names"
        ]))
    
    # /balance command
    def balance(self, update: Update, context) -> None:
        balance = self.model.get_balance()
        self.view.reply_balance(update, balance)

    # /cancel_last command
    def cancel_last(self, update: Update, context) -> None:
        expense = self.model.db.delete_last_expense()
        # return to previous balance
        balance = self.model.get_balance()
        self.model.set_balance(balance + expense.amount)
        self.view.reply_cancel(update, expense)

    # /categories command
    def categories(self, update: Update, context) -> None:
        response = f"Categories:\n"
        for idx, category in enumerate(self.model.db.get_categories(), start=1):
            name = category.name
            aliases = category.aliases
            response += f"{idx}. {name.capitalize()}: {', '.join(aliases)}\n"
        self.view.reply(update, response)
    
    # match text message type to corresponding reply or error
    def handle_message(self, update: Update, context) -> None:
        message = update.message.text
        command = command_type(message)
        try:
            match command:
                case Command.EXPENSE:
                    categories = self.model.db.get_categories()
                    expense = parse_expense(message, categories)
                    # update data in model
                    self.model.db.add_expense(expense)
                    balance = self.model.get_balance()
                    self.model.set_balance(balance - expense.amount)
                    self.view.reply_expense(update, expense)

                case Command.INCOME:
                    income = parse_income(message)
                    # update data in model
                    self.model.db.add_income(income)
                    balance = self.model.get_balance()
                    self.model.set_balance(balance + income.amount)
                    self.view.reply_income(update, income)

                case Command.SET_BALANCE:
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
        dp.add_handler(CommandHandler("cancel_last", self.cancel_last, filters=self.user_filter))

        # filter out /command messages
        dp.add_handler(MessageHandler(Filters.text & (~Filters.command) & self.user_filter, self.handle_message))
        
        # start polling updates from Telegram servers
        print("Bot running...")
        self.updater.start_polling(poll_interval=poll_interval, timeout=timeout)
        self.updater.idle()