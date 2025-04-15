from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.types import ReplyKeyboardRemove
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

import app.keyboards as kb
import app.database.requests as requests

from app.handlers.main_handlers import router

class DeleteWords(StatesGroup):
    module_id = State()
    module_name = State()

@router.message(F.text == 'Удалить модуль или слово в модуле')
async def show_modules_to_delete(message: Message, state: FSMContext):
    await message.delete()
    await message.answer('⌛️Подготавливаю список модулей...', reply_markup=ReplyKeyboardRemove())

    await message.answer("Выберите модуль, который вы хотите удалить или модуль, в котором хотите удалить слово", 
                          reply_markup=await kb.show_modules(message.from_user.id, kb.ShowModulesStates.TO_DELETE))
    await state.set_state(DeleteWords.module_id)

@router.callback_query(F.data.startswith('dltmdl_'))
async def delete_module(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    _module_id = callback.data.removeprefix('dltmdl_').strip()
    
    if not _module_id:
        await callback.message.answer("⚠️ Ошибка: имя модуля не распознано!")
        return

    _module_name = await requests.get_module_name_by_id(callback.from_user.id, int(_module_id))
    await state.update_data(module_id=_module_id)
    await state.update_data(module_name=_module_name)

    await callback.message.answer(f"Вы хотите удалить весь модуль '{_module_name}' или конкретное слово в нем?\n",
                                  reply_markup=kb.delete_module_or_word)

@router.callback_query(F.data == 'delete_all_module')
async def delete_all_module(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    module_id = data.get('module_id')
    module_name = data.get('module_name')

    if not module_id:
        await callback.message.answer("⚠️ Ошибка: модуль не выбран.")
        await state.clear()
        return

    await callback.message.answer(f"⌛️ Удаление модуля '{module_name}', это может занять некоторое время...")
 
    await requests.delete_module(callback.from_user.id, int(module_id))
    
    await callback.message.answer(f"✅ Модуль '{module_name}' успешно удален!\n",
                                  reply_markup=kb.to_start_menu)
    await state.clear()

@router.callback_query(F.data == 'delete_current_word')
async def delete_current_word(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    module_id = data.get('module_id')
    module_name = data.get('module_name')

    if not module_id:
        await callback.message.answer("⚠️ Ошибка: модуль не выбран.")
        await state.clear()
        return

    await callback.message.answer(f"Выберите слово-перевод, которые вы хотите удалить из модуля '{module_name}'",
                                  reply_markup = await kb.show_words(int(module_id)))

@router.callback_query(F.data.startswith('dltwrd_'))
async def delete_word(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    module_id = data.get('module_id')
    module_name = data.get('module_name')
    
    word_id = int(callback.data.removeprefix('dltwrd_').strip())
    word_name = await requests.get_word_by_id(int(module_id), int(word_id))

    await requests.delete_word(int(module_id), int(word_id))
    
    await callback.message.answer(f"✅ Слово '{word_name.word}' и перевод '{word_name.translation}' " + \
                                  f"успешно удалены из модуля '{module_name}'!\n",
                                  reply_markup=kb.to_start_menu)
    await state.clear()