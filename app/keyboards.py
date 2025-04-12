from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton, 
                            InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

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