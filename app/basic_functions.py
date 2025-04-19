from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.types import ReplyKeyboardRemove
from enum import Enum

class MessageType(Enum):
    MESSAGE = 0
    CALLBACK = 1

class ClearType(Enum):
    CLEAR = 0
    NOT_CLEAR = 1

class KeyboardType(Enum):
    REPLY = 0
    INLINE = 1
    NONE = 2

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

def get_start_message_text():
    return "Здравствуйте! Приглашаем вас использовать Telegram-бота, выполняющего функции личного Quizlet'а!\n" + \
           "С помощью этого бота вы можете быстрее запоминать слова, используя функционал приложения Quizlet, " + \
           "без необходимости создавать отдельный аккаунт или скачивать приложение на телефон.\n" + \
           "Предлагаю начать"

async def change_message(state: FSMContext, source, message_type, message_text, _reply_markup=None, 
                         _parse_mode=None, clear_type = ClearType.NOT_CLEAR):
    data = await state.get_data()
    last_message_id = None
    keyboard_type = 'none'
    if 'main_message_id' in data: last_message_id = (await state.get_data())['main_message_id']
    if 'keyboard_type' in data: keyboard_type = (await state.get_data())['keyboard_type']

    if clear_type == ClearType.CLEAR:
        await state.clear()
    
    is_reply_markup = isinstance(_reply_markup, ReplyKeyboardMarkup)

    curr_message = None
    if message_type == MessageType.MESSAGE:
        if not last_message_id or is_reply_markup or keyboard_type == "start" or \
           message_text == get_start_message_text() or \
           not is_reply_markup and keyboard_type == "reply":
            #print("I am here", keyboard_type)
            if last_message_id and not keyboard_type == "start": await source.bot.delete_message(source.chat.id, last_message_id)

            curr_message = await source.bot.send_message(chat_id=source.chat.id,
                                                        text=message_text,
                                                        reply_markup=_reply_markup,
                                                        parse_mode=_parse_mode)
        else:
            curr_message = await source.bot.edit_message_text(chat_id=source.chat.id,
                                                               message_id=last_message_id,
                                                               text=message_text,
                                                               reply_markup=_reply_markup,
                                                               parse_mode=_parse_mode)
    elif message_type == MessageType.CALLBACK:
        if not last_message_id or is_reply_markup or \
           not is_reply_markup and keyboard_type == "reply":
            if last_message_id: await source.bot.delete_message(source.from_user.id, last_message_id)
            curr_message = await source.bot.send_message(chat_id=source.message.chat.id,
                                                         text=message_text,
                                                         reply_markup=_reply_markup,
                                                         parse_mode=_parse_mode)
        else:
            curr_message = await source.bot.edit_message_text(chat_id=source.message.chat.id,
                                                              message_id=last_message_id,
                                                              text=message_text,
                                                              reply_markup=_reply_markup,
                                                              parse_mode=_parse_mode)
        
    await state.update_data(main_message_id=curr_message.message_id)
    
    if message_text == get_start_message_text():
        await state.update_data(keyboard_type="start")
    elif isinstance(_reply_markup, InlineKeyboardMarkup):
        await state.update_data(keyboard_type="inline")
    elif isinstance(_reply_markup, ReplyKeyboardMarkup):
        await state.update_data(keyboard_type="reply")
    else:
        await state.update_data(keyboard_type="none")