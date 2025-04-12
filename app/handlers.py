from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove

import app.keyboards as kb
import app.database.requests as requests

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
    await message.delete()

@router.message(F.text == 'Создать новый модуль')
async def create_module(message: Message, state: FSMContext):
    await message.answer("Введите название модуля", reply_markup=ReplyKeyboardRemove())
    await state.set_state(CreateModule.name)
    
@router.message(CreateModule.name)
async def module_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    module_name = message.text #(await state.get_data())['name']
    #await requests.set_module(message.from_user.id, module_name)

    await message.answer(f"Модуль {module_name} успешно создан!\n", reply_markup=kb.to_start_menu)
    #await state.set_state(CreateWord.word)

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
    
    await message.answer(
        f"Слово '{word}' с переводом '{translation}' успешно добавлено в модуль '{module_name}'\n"
        "Вы можете продолжить работу с ботом, выбрав один из пунктов меню",
        reply_markup=kb.to_start_menu
    )

    #await state.clear()