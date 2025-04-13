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
    module_name = State()
    word_list = State()
    current_word_index = State()
    true_answers_indexes = State()

@router.message(F.text == 'Повторить карточки конкретного модуля')
async def show_modules_to_repeat(message: Message, state: FSMContext):
    await message.answer('Подготавливаю список модулей...', reply_markup=ReplyKeyboardRemove())

    await message.answer("Выберите модуль, карточки которого вы хотите повторить", 
                         reply_markup=await kb.show_modules(message.from_user.id, kb.ShowModulesStates.TO_REPEAT))
    await message.delete()

async def state_setup(state: FSMContext, module_name: str, words: list):
    await state.set_data({
        'module_name': module_name,
        'word_list': words,
        'current_word_index': 0,
        'true_answers_indexes': []
    })

@router.callback_query(F.data.startswith('repeat_module__'))
async def repeat_module(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    module_name = callback.data[15:]
    words = await requests.get_words(callback.from_user.id, module_name)

    await state_setup(state, module_name, words)

    await callback.message.answer(f"Вы выбрали модуль '{module_name}', вы готовы начать повторять краточки?",
                                  reply_markup=kb.start_repeat_cards)
    
@router.callback_query(F.data.in_(['start_repeat_cards', 
                                   'correct_translation', 
                                   'incorrect_translation',
                                   'continue_repeat_cards']))
async def repeat_cards(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()

    module_name = data.get('module_name')
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
        
        word = basicFuns.escape_md2(words[_current_word_index][0])
        translation = basicFuns.escape_md2(words[_current_word_index][1])

        answer = f"Слово '{word}'\nПеревод: '||{translation}||'"

        await callback.message.answer(answer, 
                                      reply_markup=kb.cards_keyboad,
                                      parse_mode='MarkdownV2')
        
        await state.update_data(current_word_index=_current_word_index + 1)
    else:
        len_words = len(words)
        len_true_answers = len(true_indexes)
        percentage = round((len_true_answers / len_words) * 100, 2) if len_words > 0 else 0

        if percentage < 100:
            await callback.message.answer(f"Вы прошли карточки на {percentage}%!\n",
                                    reply_markup=kb.cards_end_keyboard)
            
            words = basicFuns.delete_current_indexes(words, true_indexes)
            await state_setup(state, module_name, words)
        else:
            await callback.message.answer(f"Вы прошли все карточки на все {percentage}%!\nГерой сионизма!\n",
                                    reply_markup=kb.to_start_menu)
