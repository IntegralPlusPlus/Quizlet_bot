from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.types import ReplyKeyboardRemove
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

import app.keyboards as kb
import app.database.requests as requests
import app.basic_functions as basicFuns

from app.handlers.main_handlers import router

class DeleteWords(StatesGroup):
    module_id = State()
    module_name = State()

@router.message(F.text == 'Удалить модуль или слово в модуле')
async def show_modules_to_delete(message: Message, state: FSMContext):
    await message.delete()
    await basicFuns.change_message(state,
                                   message,
                                   basicFuns.MessageType.MESSAGE,
                                   "Выберите модуль, который вы хотите удалить или модуль, в котором хотите удалить слово",
                                   await kb.show_modules(message.from_user.id, kb.ShowModulesStates.TO_DELETE))

@router.callback_query(F.data.startswith('dltmdl_'))
async def delete_module(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    _module_id = callback.data.removeprefix('dltmdl_').strip()

    _module_name = await requests.get_module_name_by_id(callback.from_user.id, int(_module_id))
    await state.update_data(module_id=_module_id)
    await state.update_data(module_name=_module_name)

    await basicFuns.change_message(state,
                                   callback,
                                   basicFuns.MessageType.CALLBACK,
                                   f"Вы хотите удалить весь модуль '{_module_name}' или конкретное слово в нем?\n",
                                   kb.delete_module_or_word)

@router.callback_query(F.data == 'delete_all_module')
async def delete_all_module(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    module_id = data.get('module_id')
    module_name = data.get('module_name')
 
    await requests.delete_module(callback.from_user.id, int(module_id))
    
    await basicFuns.change_message(state,
                                   callback,
                                   basicFuns.MessageType.CALLBACK,
                                   f"✅ Модуль '{module_name}' успешно удален!\n",
                                   kb.to_start_menu)

@router.callback_query(F.data == 'delete_current_word')
async def delete_current_word(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    module_id = data.get('module_id')
    module_name = data.get('module_name')

    await basicFuns.change_message(state,
                                   callback,
                                   basicFuns.MessageType.CALLBACK,
                                   f"Выберите слово-перевод, которые вы хотите удалить из модуля '{module_name}'",
                                   await kb.show_words(int(module_id)))

@router.callback_query(F.data.startswith('dltwrd_'))
async def delete_word(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    module_id = data.get('module_id')
    module_name = data.get('module_name')
    
    word_id = int(callback.data.removeprefix('dltwrd_').strip())
    word_name = await requests.get_word_by_id(int(module_id), int(word_id))
    await requests.delete_word(int(module_id), int(word_id))
    
    await basicFuns.change_message(state,
                                   callback,
                                   basicFuns.MessageType.CALLBACK,
                                   f"✅ Слово '{word_name.word}' и перевод '{word_name.translation}' " + \
                                   f"успешно удалены из модуля '{module_name}'!\n",
                                   kb.to_start_menu)