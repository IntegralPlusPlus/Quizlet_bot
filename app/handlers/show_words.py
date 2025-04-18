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
    last_message_id = (await state.get_data())['main_message_id']
    await message.bot.delete_message(message.chat.id, last_message_id)
    
    curr_message = await message.bot.send_message(chat_id=message.chat.id,
                                                  text="Выберите модуль, в котором хотите вывести все слова и их переводы",
                                                  reply_markup=await kb.show_modules(message.from_user.id, 
                                                                                     kb.ShowModulesStates.TO_PRINT_MODULE))
    await state.update_data(main_message_id=curr_message.message_id)

@router.callback_query(F.data.startswith('prntmdl__'))
async def print_words_in_module(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    last_message_id = (await state.get_data())['main_message_id']
    await callback.bot.delete_message(callback.from_user.id, last_message_id)

    module_id = int(callback.data.removeprefix('prntmdl__').strip())

    words = await requests.get_words(module_id)
    words_str = basicFuns.get_words_to_print(words)
    curr_message = await callback.message.answer(words_str, reply_markup=kb.to_start_menu)
    await state.update_data(main_message_id=curr_message.message_id)