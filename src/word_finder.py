from collections import Counter
import re
from math import floor
from loc_finder import get_locations

NUM_LETTERS = 10

def removeChars(string: str, chars: str):
    pat = re.compile(rf'[{chars}]')
    return re.sub(pat, '', string)

wordsf = open("./src/word_list.txt", "r", encoding="utf-8")
guessf = open("./src/guess_list.txt", "r", encoding="utf-8")

guessList = [word.strip() for word in guessf.readlines()]
text = wordsf.read()
wordList = text.splitlines()
text = text.replace('\n', '')

def get_most_common_letters():
    counts = Counter(text)
    most_common = counts.most_common(NUM_LETTERS)
    return [char for char, _ in most_common]

most_common = get_most_common_letters()

most_common_letters = ''.join([char for char in most_common])

def getWordsWithMostCommonLetters():
    words = []
    for word in wordList:
        add = True
        if len(set(word)) != 5:
            continue
        for char in word:
            if char not in most_common_letters:
                add = False
                break
        if add:
            words.append(word)
    return words

def find_words(letters_in_word):
    if letters_in_word == '': # can't find words containing no letters
        return ([], '')
    letters = letters_in_word # copy arg
    words = [] # init words array
    print(f'called letters: {letters}')
    for word in filtered_words:
        if len(set(word) & set(letters)) == 5:
            found_words = find_words(removeChars(string=letters, chars=word)) # find words with remainder of letters
            if found_words[1] != '': # only return if found full set of words
                continue
            
            print(f'word: {word}')
            print(f'found words: {found_words[0]}')
            print(f'remaining letters: {found_words[1]}')
            
            words.append(word)
            words += found_words[0]
            letters = removeChars(letters, word)
            print(f'len words: {len(words)}')
            if len(words) == floor(NUM_LETTERS/5):
                print('found all words')
                break
            break
    return (words, letters)

def get_word(pos_letters_in_word: dict[str, list[int]], word=['' for _ in range(5)]):
    print(f'called word({word})')
    if all(char != '' for char in word):
        print(f'word: {word}')
        print('word complete')
        word_str = ''.join(word)
        if word_str in guessList:
            return word_str
        return None
    for char in pos_letters_in_word.keys():
        sorted_pos_vals = pos_letters_in_word[char]
        for val in sorted_pos_vals:
            if word[val] == '':
                word[val] = char
                temp_pos_vals = pos_letters_in_word.copy()
                del temp_pos_vals[char]
                word_res = get_word(temp_pos_vals, word) 
                if word_res is None:
                    word[val] = ''
                    continue
                return word_res
        print('new char')
    return None

def find_words_with_pos(letters_in_word, sorted_pos):
    if letters_in_word == '':
        return []
    pos_letters_in_word = {char: sorted_pos[char] for char in letters_in_word}
    word = get_word(pos_letters_in_word)
    other_words = find_words_with_pos(removeChars(letters_in_word, word), sorted_pos)
    return [word] + other_words


#filtered_words = getWordsWithMostCommonLetters()
#print(find_words(most_common_letters))

words = find_words_with_pos(most_common_letters, get_locations())
print(words)

wordsf.close()
guessf.close()
