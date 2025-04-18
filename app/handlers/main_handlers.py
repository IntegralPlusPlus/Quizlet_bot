from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove

import app.keyboards as kb
import app.database.requests as requests
import app.basic_functions as basicFuns

router = Router()

@router.message(CommandStart())
async def start_menu(message: Message, state: FSMContext):
    #await state.clear()
    await requests.set_user(message.from_user.id, message.from_user.username)
    await basicFuns.change_message(state,
                                   message,
                                   basicFuns.MessageType.MESSAGE,
                                   "Здравствуйте! Приглашаем вас использовать Telegram-бота," + \
                                   "выполняющего функции личного Quizlet'а!\nПредлагаю начать",
                                   kb.start_menu,
                                   clear_type=basicFuns.ClearType.CLEAR)

    await message.delete()    

@router.callback_query(F.data == 'to_start_menu')
async def main_menu(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await basicFuns.change_message(state,
                                   callback,
                                   basicFuns.MessageType.CALLBACK,
                                   "Выберите один из пунктов меню:",
                                   kb.start_menu,
                                   clear_type=basicFuns.ClearType.CLEAR)