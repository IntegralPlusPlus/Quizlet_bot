from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton, 
                            InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from app.database.models import Module, Word
import app.database.requests as requests

start_menu = ReplyKeyboardMarkup(
    keyboard = [
        [KeyboardButton(text = 'Создать новый модуль')],
        [KeyboardButton(text = 'Добавить слово в существующий модуль')],
        [KeyboardButton(text = 'Повторить уже существующий модуль')],
    ],
    resize_keyboard = True, input_field_placeholder = "Выберите нужный пункт меню..."
)

to_start_menu = InlineKeyboardMarkup(
    inline_keyboard = [
        [InlineKeyboardButton(text = 'Вернуться в главное меню', callback_data = 'to_start_menu'),
         InlineKeyboardButton(text = 'Добавить новое слово в модуль', callback_data = 'add_word')],
    ],
)

async def show_modules_keyboard(user_id):
    modules = await requests.get_modules(user_id)
    print(modules)
    keyboard = InlineKeyboardBuilder()
    
    for module in modules:
        keyboard.add(InlineKeyboardButton(text = module, callback_data = f"module_{module}"))
    keyboard.add(InlineKeyboardButton(text = 'На главную', callback_data = 'to_start_menu'))

    return keyboard.adjust(1).as_markup()