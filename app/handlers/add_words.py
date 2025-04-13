from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.types import ReplyKeyboardRemove
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

import app.keyboards as kb
import app.database.requests as requests

from app.handlers.main_handlers import router, CHANGE_DATABASE

class CreateModule(StatesGroup):
    name = State()
    word = State()
    translation = State()

@router.message(F.text == 'Создать новый модуль')
async def create_module(message: Message, state: FSMContext):
    await message.answer("Введите название модуля", reply_markup=ReplyKeyboardRemove())
    await state.set_state(CreateModule.name)

@router.message(F.text == 'Добавить слово в существующий модуль')
async def show_modules_to_add_words(message: Message):
    await message.answer('Подготавливаю список модулей...', reply_markup=ReplyKeyboardRemove())

    await message.answer("Выберите модуль, в который хотите добавить слово", 
                         reply_markup=await kb.show_modules(message.from_user.id, kb.ShowModulesStates.TO_ADD_WORDS))
    await message.delete()

@router.callback_query(F.data.startswith('add_word_module__'))
async def add_word_to_current_module(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    module_name = callback.data[17:]

    await state.update_data(name=module_name)
    await callback.message.answer(f"Вы выбрали модуль '{module_name}'.\nВведите слово, которое вы хотите добавить в модуль", 
                                  reply_markup=ReplyKeyboardRemove())
    await state.set_state(CreateModule.word)

@router.message(CreateModule.name)
async def module_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    module_name = message.text
    
    if CHANGE_DATABASE:
        await requests.set_module(message.from_user.id, module_name)

    await message.answer(f"Модуль '{module_name}' успешно создан!\n", reply_markup=kb.add_new_word_to_module)

@router.callback_query(F.data == 'add_word')
async def add_word(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("Введите слово, которое вы хотите добавить в модуль", reply_markup=ReplyKeyboardRemove())
    await state.set_state(CreateModule.word)

@router.message(CreateModule.word)
async def add_translation(message: Message, state: FSMContext):
    await state.update_data(word=message.text)
    await message.answer("Введите перевод слова")
    await state.set_state(CreateModule.translation)

@router.message(CreateModule.translation)
async def write_word_and_translation(message: Message, state: FSMContext):
    await state.update_data(translation=message.text)
    data = await state.get_data()
    module_name = data.get('name')
    word = data.get('word')
    translation = data.get('translation')

    if CHANGE_DATABASE:
        await requests.set_word(message.from_user.id, module_name, word, translation)

    await message.answer(
        f"Слово '{word}' с переводом '{translation}' успешно добавлено в модуль '{module_name}'\n"
        "Вы можете продолжить работу с ботом, выбрав один из пунктов меню",
        reply_markup=kb.add_new_word_to_module)