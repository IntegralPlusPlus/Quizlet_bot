from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton, 
                            InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from app.database.models import Module, Word
import app.database.requests as requests
from enum import Enum

class ShowModulesStates(Enum):
    TO_ADD_WORDS = 0
    TO_PRINT_MODULE = 1
    TO_DELETE = 2

start_menu = ReplyKeyboardMarkup(
    keyboard = [
        [KeyboardButton(text = 'Создать новый модуль')],
        [KeyboardButton(text = 'Добавить слово в существующий модуль')],
        [KeyboardButton(text = 'Показать слова в модуле')],
        [KeyboardButton(text = 'Повторить уже существующий модуль')],
        [KeyboardButton(text = 'Удалить модуль')],
    ],
    resize_keyboard = True, input_field_placeholder = "Выберите нужный пункт меню..."
)

add_new_word_to_module = InlineKeyboardMarkup(
    inline_keyboard = [
        [InlineKeyboardButton(text = 'Вернуться в главное меню', callback_data = 'to_start_menu'),
         InlineKeyboardButton(text = 'Добавить новое слово в модуль', callback_data = 'add_word')],
    ],
)

to_start_menu = InlineKeyboardMarkup(
    inline_keyboard = [[InlineKeyboardButton(text = 'Вернуться в главное меню', callback_data = 'to_start_menu')]],
)

async def show_modules(user_id, show_status):
    modules = await requests.get_modules(user_id)
    keyboard = InlineKeyboardBuilder()
    
    callback_start_str = ""
    if show_status == ShowModulesStates.TO_ADD_WORDS:
        callback_start_str = "add_word_module__"
    elif show_status == ShowModulesStates.TO_PRINT_MODULE:
        callback_start_str = "print_module__"
    elif show_status == ShowModulesStates.TO_DELETE:
        callback_start_str = "delete_module__"

    for module in modules:
        keyboard.add(InlineKeyboardButton(text = module, callback_data = callback_start_str + f"{module}"))

    keyboard.add(InlineKeyboardButton(text = 'На главную', callback_data = 'to_start_menu'))

    return keyboard.adjust(1).as_markup()