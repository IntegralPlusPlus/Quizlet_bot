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
    await message.answer('Подготавливаю список модулей...', reply_markup=ReplyKeyboardRemove())

    await message.answer("Выберите модуль, карточки которого вы хотите повторить", 
                         reply_markup=await kb.show_modules(message.from_user.id, kb.ShowModulesStates.TO_REPEAT))
    await message.delete()

async def state_setup(state: FSMContext, module_id: int, words: list):
    await state.set_data({
        'module_id': module_id,
        'word_list': words,
        'current_word_index': 0,
        'true_answers_indexes': []
    })

@router.callback_query(F.data.startswith('rptmdl_'))
async def repeat_module(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    module_id = int(callback.data.removeprefix('rptmdl_').strip())
    if not module_id:
        await callback.message.answer("⚠️ Ошибка: имя модуля не распознано!")
        return

    words = await requests.get_words(module_id)
    await state_setup(state, module_id, words)
    module_name = await requests.get_module_name_by_id(callback.from_user.id, module_id)

    await callback.message.answer(f"Вы выбрали модуль '{module_name}', вы готовы начать повторять краточки?",
                                  reply_markup=kb.start_repeat_cards)
    
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
        
        word = basicFuns.escape_md2(words[_current_word_index].word)
        translation = basicFuns.escape_md2(words[_current_word_index].translation)

        answer = f"Слово '{word}'\nПеревод: '||{translation}||'"

        await callback.message.answer(answer, 
                                      reply_markup=kb.cards_keyboad,
                                      parse_mode='MarkdownV2')
        
        await state.update_data(current_word_index=_current_word_index + 1)
    else:
        len_words = len(words)
        if len_words == 0:
            await callback.message.answer("⚠️ Карточки не найдены, модуль пустой",
                                          reply_markup=kb.to_start_menu)
        else:
            len_true_answers = len(true_indexes)
            percentage = round((len_true_answers / len_words) * 100, 2) if len_words > 0 else 0

            if percentage < 100:
                await callback.message.answer(f"Вы прошли карточки на {percentage}%!\n",
                                        reply_markup=kb.cards_end_keyboard)
                
                words = basicFuns.delete_current_indexes(words, true_indexes)
                await state_setup(state, module_id, words)
            else:
                await callback.message.answer(f"Вы прошли все карточки на все {percentage}%!\nГерой сионизма!",
                                        reply_markup=kb.to_start_menu)
