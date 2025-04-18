from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.types import ReplyKeyboardRemove
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

import app.keyboards as kb
import app.database.requests as requests
import app.basic_functions as basicFuns

from app.handlers.main_handlers import router

class RepeatWords(StatesGroup):
    module_id = State()
    word_list = State()
    current_word_index = State()
    true_answers_indexes = State()

@router.message(F.text == 'Повторить карточки конкретного модуля')
async def show_modules_to_repeat(message: Message, state: FSMContext):
    await message.delete()
    last_message_id = (await state.get_data())['main_message_id']
    await message.bot.delete_message(message.chat.id, last_message_id)

    modules_keyboard = await kb.show_modules(message.from_user.id, kb.ShowModulesStates.TO_REPEAT)
    curr_message = await message.bot.send_message(
                        chat_id=message.chat.id,
                        text = "Выберите модуль, карточки которого вы хотите повторить",
                        reply_markup=modules_keyboard)
    await state.update_data(main_message_id=curr_message.message_id)

async def state_setup(state: FSMContext, message_id: int, module_id: int, words: list):
    await state.set_data({
        'main_message_id': message_id,
        'module_id': module_id,
        'word_list': words,
        'current_word_index': 0,
        'true_answers_indexes': []
    })

@router.callback_query(F.data.startswith('rptmdl_'))
async def repeat_module(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    last_message_id = (await state.get_data())['main_message_id']
    await callback.bot.delete_message(callback.from_user.id, last_message_id)
    module_id = int(callback.data.removeprefix('rptmdl_').strip())

    words = await requests.get_words(module_id)
    module_name = await requests.get_module_name_by_id(callback.from_user.id, module_id)

    curr_message = await callback.message.answer(f"Вы выбрали модуль '{module_name}', вы готовы начать повторять краточки?",
                                                  reply_markup=kb.start_repeat_cards)
    
    await state_setup(state, curr_message.message_id, module_id, words)
    
@router.callback_query(F.data.in_(['start_repeat_cards', 
                                   'correct_translation', 
                                   'incorrect_translation',
                                   'continue_repeat_cards']))
async def repeat_cards(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    last_message_id = (await state.get_data())['main_message_id']
    await callback.bot.delete_message(callback.from_user.id, last_message_id)
    data = await state.get_data()

    module_id = data.get('module_id')
    words = data.get('word_list', [])
    _current_word_index = data.get('current_word_index')
    true_indexes = data.get('true_answers_indexes', [])

    if callback.data == 'correct_translation':
        true_indexes.append(_current_word_index - 1)
        await state.update_data(true_answers_indexes=true_indexes)

    if _current_word_index < len(words):
        answer = ""
        if _current_word_index == 0:
            answer = "Начинаем повторять карточки!\n"
        
        word = basicFuns.escape_md2(words[_current_word_index].word)
        translation = basicFuns.escape_md2(words[_current_word_index].translation)

        answer = f"Слово '{word}'\nПеревод: '||{translation}||'"

        curr_message = await callback.message.answer(answer, 
                                      reply_markup=kb.cards_keyboad,
                                      parse_mode='MarkdownV2')
        
        await state.update_data(main_message_id=curr_message.message_id)
        await state.update_data(current_word_index=_current_word_index + 1)
    else:
        len_words = len(words)
        if len_words == 0:
            curr_message = await callback.message.answer("⚠️ Карточки не найдены, модуль пустой",
                                                         reply_markup=kb.to_start_menu)
            await state.update_data(main_message_id=curr_message.message_id)
        else:
            len_true_answers = len(true_indexes)
            percentage = round((len_true_answers / len_words) * 100, 2) if len_words > 0 else 0

            if percentage < 100:
                curr_message = await callback.message.answer(f"Вы прошли карточки на {percentage}%!\n",
                                                             reply_markup=kb.cards_end_keyboard)
                
                words = basicFuns.delete_current_indexes(words, true_indexes)
                await state_setup(state, curr_message.message_id, module_id, words)
            else:
                curr_message = await callback.message.answer(f"Вы прошли все карточки на все {percentage}%!\nГерой сионизма!",
                                                             reply_markup=kb.to_start_menu)
                await state.update_data(main_message_id=curr_message.message_id)
