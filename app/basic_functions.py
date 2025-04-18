from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from enum import Enum

class MessageType(Enum):
    MESSAGE = 0
    CALLBACK = 1

LRM = "\u200E" # Left-to-right mark for Hebrew text

def get_words_to_print(words):
    if words is None:
        return "В модуле пока нет слов"
    
    result = "Слова в модуле:\n"
    index = 1
    for word in words:
        result += f"{index}) {LRM}{word.word} - {LRM}{word.translation}\n"
        index += 1
    
    return result

def escape_md2(text: str) -> str:
    escape_chars = r'\_*[]()~`>#+-=|{}.!'
    return ''.join(f'\\{c}' if c in escape_chars else c for c in text)

def delete_current_indexes(my_list, indexes):
    return [item for i, item in enumerate(my_list) if i not in indexes]

async def change_message(state: FSMContext, message, message_type, message_text, _reply_markup=None):
    last_message_id = (await state.get_data())['main_message_id']

    curr_message = None

    if message_type == MessageType.MESSAGE:
        if last_message_id: await message.bot.delete_message(message.chat.id, last_message_id)
        curr_message = await message.bot.send_message(chat_id=message.chat.id,
                                                      text=message_text,
                                                      reply_markup=_reply_markup)
    elif message_type == MessageType.CALLBACK:
        if last_message_id: await message.bot.delete_message(message.from_user.id, last_message_id)
        curr_message = await message.message.answer(text=message_text,
                                                    reply_markup=_reply_markup)
        
    await state.update_data(main_message_id=curr_message.message_id)
        