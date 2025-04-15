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