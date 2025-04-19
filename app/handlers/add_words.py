from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.types import ReplyKeyboardRemove
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

import app.keyboards as kb
import app.database.requests as requests
import app.basic_functions as basicFuns

from app.handlers.main_handlers import router

class CreateModule(StatesGroup):
    name = State()
    word = State()
    translation = State()

@router.message(F.text == 'Создать новый модуль')
async def create_module(message: Message, state: FSMContext):
    await message.delete()
    await basicFuns.change_message(state,
                                   message,
                                   basicFuns.MessageType.MESSAGE,
                                   "Введите название модуля",
                                   ReplyKeyboardRemove())


    await state.set_state(CreateModule.name)

@router.message(F.text == 'Добавить слово в существующий модуль')
async def show_modules_to_add_words(message: Message, state: FSMContext):
    await message.delete()
    await basicFuns.change_message(state,
                                   message,
                                   basicFuns.MessageType.MESSAGE,
                                   "Выберите модуль, в который хотите добавить слово",
                                   await kb.show_modules(message.from_user.id, kb.ShowModulesStates.TO_ADD_WORDS))

@router.callback_query(F.data.startswith('addwrdmdl_'))
async def add_word_to_current_module(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    module_id = int(callback.data.removeprefix('addwrdmdl_').strip())
    module_name = await requests.get_module_name_by_id(callback.from_user.id, module_id)

    await state.update_data(name=module_name)
    await basicFuns.change_message(state,
                                   callback,
                                   basicFuns.MessageType.CALLBACK,
                                   f"Вы выбрали модуль '{module_name}'.\nВведите слово, которое вы хотите добавить в модуль",
                                   ReplyKeyboardRemove())
    await state.set_state(CreateModule.word)

@router.message(CreateModule.name)
async def module_name(message: Message, state: FSMContext):
    await message.delete()
    await state.update_data(name=message.text)
    module_name = message.text
    
    await requests.set_module(message.from_user.id, message.from_user.username, module_name)

    await basicFuns.change_message(state,
                                   message,
                                   basicFuns.MessageType.MESSAGE,
                                   f"✅ Модуль '{module_name}' успешно создан!",
                                   kb.add_new_word_to_module)

@router.callback_query(F.data == 'add_word')
async def add_word(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await basicFuns.change_message(state,
                                   callback,
                                   basicFuns.MessageType.CALLBACK,
                                   "Введите слово, которое вы хотите добавить в модуль",
                                   ReplyKeyboardRemove())
    await state.set_state(CreateModule.word)

@router.message(CreateModule.word)
async def add_translation(message: Message, state: FSMContext):
    await message.delete()
    await state.update_data(word=message.text)
    await basicFuns.change_message(state,
                                   message,
                                   basicFuns.MessageType.MESSAGE,
                                   "Введите перевод слова")
    await state.set_state(CreateModule.translation)

@router.message(CreateModule.translation)
async def write_word_and_translation(message: Message, state: FSMContext):
    await message.delete()
    await state.update_data(translation=message.text)
    data = await state.get_data()
    module_name = data.get('name')
    word = data.get('word')
    translation = data.get('translation')

    await requests.set_word(message.from_user.id, module_name, word, translation)

    await basicFuns.change_message(state,
                                   message,
                                   basicFuns.MessageType.MESSAGE,
                                   f"✅ Слово '{word}' с переводом '{translation}' успешно добавлено в модуль '{module_name}'\n"
                                   "Вы можете продолжить работу с ботом, выбрав один из пунктов меню",
                                   kb.add_new_word_to_module)