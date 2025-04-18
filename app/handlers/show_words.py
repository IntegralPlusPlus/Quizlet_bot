from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.types import ReplyKeyboardRemove
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

import app.keyboards as kb
import app.database.requests as requests
import app.basic_functions as basicFuns

from app.handlers.main_handlers import router

@router.message(F.text == 'Показать слова в модуле')
async def show_modules_to_print(message: Message, state: FSMContext):
    await message.delete()
    await basicFuns.change_message(state,
                                   message,
                                   basicFuns.MessageType.MESSAGE,
                                   "Выберите модуль, в котором хотите вывести все слова и их переводы",
                                   await kb.show_modules(message.from_user.id, kb.ShowModulesStates.TO_PRINT_MODULE))

@router.callback_query(F.data.startswith('prntmdl__'))
async def print_words_in_module(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    module_id = int(callback.data.removeprefix('prntmdl__').strip())

    words = await requests.get_words(module_id)
    words_str = basicFuns.get_words_to_print(words)
    await basicFuns.change_message(state,
                                   callback,
                                   basicFuns.MessageType.CALLBACK,
                                   words_str,
                                   kb.to_start_menu)