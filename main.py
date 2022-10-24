import os
import dotenv
from bot.controller import Controller
from bot.view import View
from bot.model import Model


def main():
    dotenv.load_dotenv(".env")
    TELEGRAM_API_KEY = os.getenv("TELEGRAM_API_KEY")
    TELEGRAM_USER_ID = int(os.getenv("TELEGRAM_USER_ID"))

    controller = Controller(
        telegram_api_key=TELEGRAM_API_KEY,
        telegram_user_id=TELEGRAM_USER_ID,
        view=View(),
        model=Model()
    )
    
    controller.start_bot()


if __name__ == "__main__":
    main()