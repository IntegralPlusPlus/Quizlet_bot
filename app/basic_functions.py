LRM = "\u200E" # Left-to-right mark for Hebrew text

def get_words_to_print(words):
    if words is None:
        return "В модуле пока нет слов"
    
    result = "Слова в модуле:\n"
    index = 1
    for word, translation in words:
        result += f"{index}) {LRM}{word} - {LRM}{translation}\n"
        index += 1
    
    return result