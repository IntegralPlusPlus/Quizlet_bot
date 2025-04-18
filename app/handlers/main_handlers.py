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
async def start_menu(message: Message, state: FSMContext):
    await state.clear()
    await requests.set_user(message.from_user.id, message.from_user.username)
    
    start_message = await message.bot.send_message(chat_id=message.chat.id,
                                                   text="Здравствуйте! Приглашаем вас использовать Telegram-бота, " + \
                                                   ", выполняющего функции личного Quizlet'а! \n" + \
                                                   'Предлагаю начать', 
                                                    reply_markup = kb.start_menu)
    
    await state.update_data(main_message_id=start_message.message_id)

    await message.delete()    

@router.callback_query(F.data == 'to_start_menu')
async def main_menu(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    last_message_id = (await state.get_data())['main_message_id']
    await callback.message.bot.delete_message(callback.from_user.id, last_message_id)
    await state.clear()

    curr_message = await callback.message.answer("Выберите один из пунктов меню:", reply_markup = kb.start_menu)
    await state.update_data(main_message_id=curr_message.message_id)