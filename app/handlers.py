from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove

import app.keyboards as kb
import app.database.requests as requests
import app.basic_functions as basicFuns

CHANGE_DATABASE = True

class CreateModule(StatesGroup):
    name = State()
    word = State()
    translation = State()

router = Router()

@router.message(CommandStart())
async def start_menu(message: Message):
    await requests.set_user(message.from_user.id)
    
    await message.answer("Здравствуйте! Приглашаем вас использовать Telegram-бота, выполняющего функции личного Quizlet'а! \n" + \
                        'Предлагаю начать', reply_markup = kb.start_menu)

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

@router.message(F.text == 'Показать слова в модуле')
async def show_modules_to_print(message: Message):
    await message.answer('Подготавливаю список модулей...', reply_markup=ReplyKeyboardRemove())

    await message.answer("Выберите модуль, в котором хотите вывести все слова и их переводы", 
                         reply_markup=await kb.show_modules(message.from_user.id, kb.ShowModulesStates.TO_PRINT_MODULE))
    await message.delete()

@router.callback_query(F.data.startswith('print_module__'))
async def print_words_in_module(callback: CallbackQuery):
    await callback.answer()
    module_name = callback.data[14:]

    words = await requests.get_words(callback.from_user.id, module_name)
    words_str = basicFuns.get_words_to_print(words)
    await callback.message.answer(words_str, reply_markup=kb.to_start_menu)

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

    await message.answer(f"Модуль {module_name} успешно создан!\n", reply_markup=kb.to_start_menu)

@router.callback_query(F.data == 'to_start_menu')
async def main_menu(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Выберите один из пунктов меню:", reply_markup = kb.start_menu)

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
        reply_markup=kb.to_start_menu)