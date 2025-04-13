from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.types import ReplyKeyboardRemove
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

import app.keyboards as kb
import app.database.requests as requests

from app.handlers.main_handlers import router
from config import CHANGE_DATABASE

class DeleteWords(StatesGroup):
    module_name = State()

@router.message(F.text == 'Удалить модуль или слово в модуле')
async def show_modules_to_delete(message: Message, state: FSMContext):
    await message.answer('Подготавливаю список модулей...', reply_markup=ReplyKeyboardRemove())

    await message.answer("Выберите модуль, который вы хотите удалить или модуль, в котором хотите удалить слово", 
                         reply_markup=await kb.show_modules(message.from_user.id, kb.ShowModulesStates.TO_DELETE))
    await message.delete()
    await state.set_state(DeleteWords.module_name)

@router.callback_query(F.data.startswith('delete_module__'))
async def delete_module(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    _module_name = callback.data[15:]

    await state.update_data(module_name=_module_name)
    await callback.message.answer(f"Вы хотите удалить весь модуль '{_module_name}' или конкретное слово в нем?\n",
                                  reply_markup=kb.delete_module_or_word)

@router.callback_query(F.data == 'delete_all_module')
async def delete_all_module(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    module_name = data.get('module_name')

    await callback.message.answer(f"⌛️ Удаление модуля '{module_name}', это может занять некоторое время...")

    if CHANGE_DATABASE:
        await requests.delete_module(callback.from_user.id, module_name)
    
    await callback.message.answer(f"Модуль '{module_name}' успешно удален!\n",
                                  reply_markup=kb.to_start_menu)
    await state.clear()

@router.callback_query(F.data == 'delete_current_word')
async def delete_current_word(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    module_name = data.get('module_name')

    await callback.message.answer(f"Выберите слово-перевод, которые вы хотите удалить из модуля '{module_name}'",
                                  reply_markup = await kb.show_words(callback.from_user.id, module_name))

@router.callback_query(F.data.startswith('delete_word__'))
async def delete_word(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    module_name = data.get('module_name')
    
    combination = callback.data[13:]
    word, translation = combination.split('|p|a|s|s|w|o|r|d|')

    if CHANGE_DATABASE:
        await requests.delete_word(callback.from_user.id, module_name, word, translation)
    
    await callback.message.answer(f"Слово '{word}' и перевод '{translation}' успешно удалены из модуля '{module_name}'!\n",
                                  reply_markup=kb.to_start_menu)
    await state.clear()