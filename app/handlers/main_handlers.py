from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove

import app.keyboards as kb
import app.database.requests as requests

router = Router()

@router.message(CommandStart())
async def start_menu(message: Message):
    await requests.set_user(message.from_user.id)
    
    await message.answer("Здравствуйте! Приглашаем вас использовать Telegram-бота, выполняющего функции личного Quizlet'а! \n" + \
                        'Предлагаю начать', reply_markup = kb.start_menu)

@router.callback_query(F.data == 'to_start_menu')
async def main_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Выберите один из пунктов меню:", reply_markup = kb.start_menu)