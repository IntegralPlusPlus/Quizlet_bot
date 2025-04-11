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
class CreateWord(StatesGroup):
    word = State()
    translation = State()

router = Router()

@router.message(CommandStart())
async def start(message: Message):
    await requests.set_user(message.from_user.id)
    await message.answer("Здравствуйте! Приглашаем вас использовать Telegram-бота, выполняющего функции личного Quizlet'а! \n" +
                         'Предлагаю начать',
                         reply_markup = kb.start_menu)
    await message.delete()

@router.message(F.text == 'Создать новый модуль')
async def create_module(message: Message, state: FSMContext):
    await message.answer("Введите название модуля", reply_markup=ReplyKeyboardRemove())
    await state.set_state(CreateModule.name)
    
@router.message(CreateModule.name)
async def module_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    module_name = (await state.get_data())['name']
    await requests.set_module(message.from_user.id, module_name)

    await message.answer(f"Модуль {module_name} успешно создан!\n", reply_markup=kb.start_menu)

"""    
@router.message(CreateWord.word)
async def module_word(message: Message, state: FSMContext):
    await state.update_data(word = message.text)
    await message.answer("Введите перевод")
    await state.set_state(CreateWord.translation)

@router.message(CreateWord.translation)
async def module_translation(message: Message, state: FSMContext):
    await state.update_data(translation = message.text)
    data = await state.get_data()
    name = data.get('name')
    word = data.get('word')
    translation = data.get('translation')
    
    await message.answer(f"Слово: {word}\n" +
                         f"Перевод: {translation}\n" +
                         f"Успешно добавлены в модуль: {name}\n" +
                         "Теперь вы можете продолжить работу с ботом по одному из пунктов меню")
"""