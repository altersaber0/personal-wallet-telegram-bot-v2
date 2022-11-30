from abc import ABC, abstractmethod
from typing import Callable

from telegram.update import Update
from telegram.ext import Updater, CallbackContext, BaseFilter

from ..view import View
from ..model import Model


class Controller(ABC):
    """This abstract class represents a controller in an MVC-architecture."""

    def __init__(self, updater: Updater, user_filter: BaseFilter, view: View, model: Model) -> None:
        self.updater = updater
        self.user_filter = user_filter
        self.view = view
        self.model = model
        self.blocked_mode = False
    
    @abstractmethod
    def add_handlers(self) -> None:
        """This method should add all needed telegram Handlers to the Updater.Dispatcher"""
        ...


def block_if_in_blocked_mode(func: Callable[[Controller, Update, CallbackContext], int | None]):
    """
    Execute a given method of a controller if it is not in blocked mode,
    otherwise do nothing.
    """

    def wrapper(ctr: Controller, update: Update, context: CallbackContext):
        if ctr.blocked_mode:
            return
        else:
            return func(ctr, update, context)
            
    return wrapper