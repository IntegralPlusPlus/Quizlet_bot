from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.types import ReplyKeyboardRemove
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

import app.keyboards as kb
import app.database.requests as requests
import app.basic_functions as basicFuns
import random

from app.handlers.main_handlers import router

class RepeatWords(StatesGroup):
    module_id = State()
    word_list = State()
    current_word_index = State()
    true_answers_indexes = State()

@router.message(F.text == 'Повторить карточки конкретного модуля')
async def show_modules_to_repeat(message: Message, state: FSMContext):
    await message.delete()
    await basicFuns.change_message(state,
                                   message,
                                   basicFuns.MessageType.MESSAGE,
                                   "Выберите модуль, карточки которого вы хотите повторить",
                                   await kb.show_modules(message.from_user.id, kb.ShowModulesStates.TO_REPEAT))

async def state_setup(state: FSMContext, module_id: int, words: list):
    await state.update_data(module_id= module_id)
    await state.update_data(word_list=words)
    await state.update_data(current_word_index=0)
    await state.update_data(true_answers_indexes=[])

@router.callback_query(F.data.startswith('rptmdl_'))
async def repeat_module(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    module_id = int(callback.data.removeprefix('rptmdl_').strip())
    words = await requests.get_words(module_id)
    module_name = await requests.get_module_name_by_id(callback.from_user.id, module_id)

    await basicFuns.change_message(state,
                                   callback,
                                   basicFuns.MessageType.CALLBACK,
                                   f"Вы выбрали модуль '{module_name}', вы готовы начать повторять карточки?",
                                   kb.start_repeat_cards)
    
    await state_setup(state, module_id, words)

@router.callback_query(F.data.in_(['start_repeat_cards', 
                                   'correct_translation', 
                                   'incorrect_translation',
                                   'continue_repeat_cards']))
async def repeat_cards(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
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
        
        word = words[_current_word_index].word
        await basicFuns.change_message(state,
                                       callback,
                                       basicFuns.MessageType.CALLBACK,
                                       f"Слово '{word}'",
                                       kb.show_true_answer)
        
        await state.update_data(current_word_index=_current_word_index + 1)
    else:
        len_words = len(words)
        if len_words == 0:
            await basicFuns.change_message(state,
                                           callback,
                                           basicFuns.MessageType.CALLBACK,
                                           "⚠️ Карточки не найдены, модуль пустой",
                                           kb.to_start_menu)
        else:
            len_true_answers = len(true_indexes)
            percentage = round((len_true_answers / len_words) * 100, 2) if len_words > 0 else 0

            if percentage < 100:
                await basicFuns.change_message(state,
                                               callback,
                                               basicFuns.MessageType.CALLBACK,
                                               f"Вы прошли карточки на {percentage}%!\n",
                                               kb.cards_end_keyboard)
                
                words = basicFuns.delete_current_indexes(words, true_indexes)
                await state_setup(state, module_id, words)
            else:
                await basicFuns.change_message(state,
                                               callback,
                                               basicFuns.MessageType.CALLBACK,
                                               f"Вы прошли все карточки на все {percentage}%! 😎\nГерой сионизма! ✡️",
                                               kb.to_start_menu)

@router.callback_query(F.data == 'show_true_answer')
async def show_true_answer(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()

    module_id = data.get('module_id')
    words = data.get('word_list', [])
    _current_word_index = data.get('current_word_index')
    translation = words[_current_word_index - 1].translation
    word = words[_current_word_index - 1].word
    await basicFuns.change_message(state,
                                   callback,
                                   basicFuns.MessageType.CALLBACK,
                                   f"Перевод слова '{word}': '{translation}'",
                                   kb.cards_keyboad)