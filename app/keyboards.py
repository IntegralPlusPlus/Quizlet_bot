from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton, 
                            InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from app.database.models import User, Module, Word
import app.database.requests as requests
from enum import Enum

class ShowModulesStates(Enum):
    TO_ADD_WORDS = 0
    TO_PRINT_MODULE = 1
    TO_DELETE = 2
    TO_REPEAT = 3

start_menu = ReplyKeyboardMarkup(
    keyboard = [
        [KeyboardButton(text = 'Создать новый модуль')],
        [KeyboardButton(text = 'Повторить карточки конкретного модуля')],
        [KeyboardButton(text = 'Добавить слово в существующий модуль')],
        [KeyboardButton(text = 'Показать слова в модуле')],
        [KeyboardButton(text = 'Удалить модуль или слово в модуле')],
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
        callback_start_str = "addwrdmdl_"
    elif show_status == ShowModulesStates.TO_PRINT_MODULE:
        callback_start_str = "prntmdl__"
    elif show_status == ShowModulesStates.TO_DELETE:
        callback_start_str = "dltmdl_"
    elif show_status == ShowModulesStates.TO_REPEAT:
        callback_start_str = "rptmdl_"

    for module in modules:
        keyboard.add(InlineKeyboardButton(text = module.name, callback_data = callback_start_str + f"{module.id}"))

    keyboard.add(InlineKeyboardButton(text = 'На главную', callback_data = 'to_start_menu'))

    return keyboard.adjust(1).as_markup()

delete_module_or_word = InlineKeyboardMarkup(
    inline_keyboard = [
        [InlineKeyboardButton(text = 'Удалить весь модуль', callback_data = 'delete_all_module')],
        [InlineKeyboardButton(text = 'Удалить слово в модуле', callback_data = 'delete_current_word')],
        [InlineKeyboardButton(text = 'Хочу вернуться на главную', callback_data = 'to_start_menu')],
    ],
)

async def show_words(module_id):
    words = await requests.get_words(module_id)
    keyboard = InlineKeyboardBuilder()

    for my_word in words:
        keyboard.add(InlineKeyboardButton(text = f"{my_word.word} - {my_word.translation}",
                                           callback_data = f"dltwrd_{my_word.id}"))

    keyboard.add(InlineKeyboardButton(text = 'На главную', callback_data = 'to_start_menu'))

    return keyboard.adjust(1).as_markup()

start_repeat_cards = InlineKeyboardMarkup(
    inline_keyboard = [
        [InlineKeyboardButton(text = 'Да, я готов начать 🚀', callback_data = 'start_repeat_cards')],
        [InlineKeyboardButton(text = 'На главную страницу', callback_data = 'to_start_menu')],
    ],
)

cards_keyboad = InlineKeyboardMarkup(
    inline_keyboard = [
        [InlineKeyboardButton(text = 'Знаю ✅', callback_data = 'correct_translation'),
         InlineKeyboardButton(text = 'Изучено ❌', callback_data = 'incorrect_translation')],
        [InlineKeyboardButton(text = 'На главную страницу', callback_data = 'to_start_menu')],
    ],
)

cards_end_keyboard = InlineKeyboardMarkup(
    inline_keyboard = [
        [InlineKeyboardButton(text = 'Продолжить повторение', callback_data = 'continue_repeat_cards')],
        [InlineKeyboardButton(text = 'На главную страницу', callback_data = 'to_start_menu')],
    ],
)