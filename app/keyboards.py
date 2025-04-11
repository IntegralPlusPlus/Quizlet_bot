from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton, 
                            InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

start_menu = ReplyKeyboardMarkup(
    keyboard = [
        [KeyboardButton(text = 'Создать новый модуль')],
        [KeyboardButton(text = 'Повторить уже существующий модуль')],
    ],
    resize_keyboard = True, input_field_placeholder = "Выберите нужный пункт меню..."
)