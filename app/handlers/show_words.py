from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.types import ReplyKeyboardRemove

import app.keyboards as kb
import app.database.requests as requests
import app.basic_functions as basicFuns

from app.handlers.main_handlers import router

@router.message(F.text == 'Показать слова в модуле')
async def show_modules_to_print(message: Message):
    await message.answer('Подготавливаю список модулей...', reply_markup=ReplyKeyboardRemove())

    await message.answer("Выберите модуль, в котором хотите вывести все слова и их переводы", 
                         reply_markup=await kb.show_modules(message.from_user.id, kb.ShowModulesStates.TO_PRINT_MODULE))
    await message.delete()

@router.callback_query(F.data.startswith('prntmdl__'))
async def print_words_in_module(callback: CallbackQuery):
    await callback.answer()
    module_id = int(callback.data.removeprefix('prntmdl__').strip())

    words = await requests.get_words(module_id)
    words_str = basicFuns.get_words_to_print(words)
    await callback.message.answer(words_str, reply_markup=kb.to_start_menu)