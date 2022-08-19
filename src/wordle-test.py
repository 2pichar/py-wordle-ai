import itertools
import copy
import sys
from wordle import Wordle,  WordleAI

with open('./src/guess_list.txt', encoding='utf-8') as guess_f:
    guess_list = [line.strip() for line in guess_f.readlines()]
with open('./src/word_list.txt', encoding='utf-8') as word_f:
    word_list = [line.strip() for line in word_f.readlines()]

print_file = None

def print(obj, *, end='\n', file_out=True):
    if file_out:
        global print_file
        if print_file is None:
            print_file = open('./src/wordle_out.txt', 'w', encoding='utf-8')
        __builtins__.print(obj, end=end, file=print_file)
    else:
        __builtins__.print(obj, end=end, file=sys.stdout)

# constants
WORD = sys.argv[1]

# type aliases
letter_pos_t = dict[str, int | list[int]]

def get_starting_info(word: str) -> tuple[letter_pos_t, set[str]]:
    game = Wordle()
    game.word = word
    wordle_ai = WordleAI(game)
    for _ in range(3):
        guess = wordle_ai.get_best_guess()
        wordle_ai.add_guess(game.make_guess(guess))
    wordle_ai.share_knowledge()
    return wordle_ai.sentences[0].letter_pos, wordle_ai.sentences[0].letters_unknown

class Helpers():
    WORDLE_FREQS = list('eraotilscnudpbyghmfkwvxzjq')
    def __init__(self) -> None:
        pass
    @classmethod
    def update_positions(cls, letter_pos: letter_pos_t, val):
        letter_position_dict = letter_pos.copy()
        for key, vals in list(letter_position_dict.items()):
            if isinstance(vals, int):
                continue
            if val in vals:
                vals.remove(val)
                letter_position_dict[key] = vals
        return letter_position_dict

    @classmethod
    def get_word(cls, letter_pos: letter_pos_t):
        if cls.complete(letter_pos):
            return ''.join(sorted(list(letter_pos.keys()), key=lambda l: letter_pos[l]))
        return ''

    @classmethod
    def is_word(cls, letter_pos: letter_pos_t):
        return cls.get_word(letter_pos) in guess_list

    @classmethod
    def complete(cls, letter_pos: letter_pos_t):
        return all(isinstance(val, int) for val in letter_pos.values()) and len(letter_pos) == 5

class AI():
    def __init__(self):
        pass
    def enforce_arc_consistency(self, letter_pos: letter_pos_t, letter_a: str, letter_b: str):
        x_vals = letter_pos[letter_a]
        y_vals = letter_pos[letter_b]
        if isinstance(x_vals, int):
            return False
        else:
            drop_from_x = []
            for x_val in x_vals:
                if isinstance(y_vals, int): # position of y is known
                    if x_val == y_vals: # position of y can't be in x
                        drop_from_x.append(x_val) # remove x_val from x
                else: # y_vals is a list
                    if x_val in y_vals and len(y_vals) == 1: # x_val is only possibile position for y
                        drop_from_x.append(x_val) # remove x_val from x
            for x_val in drop_from_x:
                x_vals.remove(x_val)
            letter_pos[letter_a] = x_vals
            
            if len(drop_from_x) > 0:
                return True
            return False

    def ac3(self, letter_pos: letter_pos_t, queue: set[tuple[str, str]]):
        if queue is None:
            queue = set()
        if len(queue) == 0:
            queue = {(x, y) for x in letter_pos.keys() for y in letter_pos.keys() if x != y}
        while len(queue) > 0:
            letter_a, letter_b = queue.pop()
            if self.enforce_arc_consistency(letter_pos, letter_a, letter_b):
                if isinstance(letter_pos[letter_a], list) and len(letter_pos[letter_a]) == 0:
                    return False
                new_arcs = {(y, letter_a) for y in letter_pos.keys() if y != letter_a}
                queue.update(new_arcs)
        return True

    def consistent(self, letter_pos: letter_pos_t):
        for key, val in letter_pos.items():
            if isinstance(val, int):
                for other_key, other_val in letter_pos.items():
                    if key != other_key:
                        if isinstance(other_val, list):
                            if val in other_val:
                                return False
                        else:
                            if val == other_val:
                                return False
            else:
                pass
        return True

    def get_unassigned_letter(self, letter_pos: letter_pos_t, letters_unknown: set[str]):
        '''
        returns a variable that has not yet been assigned a value
        pulls from the list of letters that are known in the word first,
        then uses the list of unknown letters
        '''
        unassigned = {key: val for key, val in letter_pos.items() if isinstance(val, list)}
        unassigned_letters = list(unassigned.keys())
        if len(unassigned) != 0:
            all_values: list[int] = list(itertools.chain([val for val in unassigned.values() if isinstance(val, list)]))
            num_uniques: dict[str, list] = {key: [val for val in unassigned[key] if all_values.count(val) == 1] for key in unassigned_letters}
            unassigned_letters.sort(key=lambda x: len(num_uniques[x]))
            return unassigned_letters[0]
        else:
            letters_in_word = list(letter_pos.keys())
            unknown_letters = list(letters_unknown - set(letters_in_word))
            unknown_letters.sort(key=Helpers.WORDLE_FREQS.index)
            if len(unknown_letters) != 0:
                return unknown_letters[0]
            return None

    def order_domain_values(self, letter_pos: letter_pos_t, letter: str) -> list[int]:
        '''
        returns the list of possible positions for the given letter,
        ordered by the number of other positions that letter would rule out
        '''
        if letter in letter_pos:
            if isinstance(letter_pos[letter], int):
                return [letter_pos[letter]]
            vals = list(letter_pos[letter])
            num_ruled_out = {val: 0 for val in vals}
            other_chars = [key for key in letter_pos.keys() if key != letter]
            for other_char in other_chars:
                if isinstance(letter_pos[other_char], int):
                    continue
                for other_val in letter_pos[other_char]:
                    if other_val in vals:
                        num_ruled_out[other_val] += 1
            vals.sort(key=lambda x: num_ruled_out[x])
            return vals
        else:
            vals = list(set(range(5)) - {letter_pos[k] for k in letter_pos if isinstance(letter_pos[k], int)})
            num_ruled_out = {val: 0 for val in vals}
            other_chars = list(letter_pos.keys())
            for other_char in other_chars:
                if isinstance(letter_pos[other_char], int):
                    continue
                for other_val in letter_pos[other_char]:
                    if other_val in vals:
                        num_ruled_out[other_val] += 1
            vals.sort(key=lambda x: num_ruled_out[x])
            return vals

    def backtrack(self, letter_pos, word_letters_unknown):
        if Helpers.complete(letter_pos):
            if self.consistent(letter_pos):
                if Helpers.is_word(letter_pos):
                    return letter_pos
            return None
        else:
            ac3_letter_pos = copy.deepcopy(letter_pos)
            #if not ac3(ac3_letter_pos):
            #    return None
            letters_unknown = word_letters_unknown.copy()
            while (char := self.get_unassigned_letter(ac3_letter_pos, letters_unknown)) is not None:
                if char in letters_unknown:
                    letters_unknown.remove(char)
                #print(char)
                #print(letters_unknown)
                domain = self.order_domain_values(ac3_letter_pos, char)
                for val in domain:
                    new_letter_pos = copy.deepcopy(ac3_letter_pos)
                    new_letter_pos[char] = val
                    new_letter_pos = Helpers.update_positions(new_letter_pos, val)
                    #print(f'word: {get_word(new_letter_pos)}')
                    if self.consistent(new_letter_pos):
                        result = self.backtrack(new_letter_pos, letters_unknown)
                        if result is not None:
                            return result
        return None

    def get_best_guess(self, letter_pos, letters_unknown):
        # score letter_pos by amount of info contained
        pos_score = 0
        for val in letter_pos.values():
            if isinstance(val, int):
                pos_score += 1
            else:
                pos_score += 1/len(val)
        print(round(pos_score, 2), file_out=False)
        if pos_score > 1.6:
            completed_pos = self.backtrack(letter_pos, letters_unknown)
            guessed_word =  Helpers.get_word(completed_pos)
            return guessed_word

def get_guess(word: str):
    if len(set(word)) != 5:
        return
    letter_pos, letters_unknown = get_starting_info(word)
    completed_pos: letter_pos_t = AI().backtrack(letter_pos, letters_unknown)
    guessed_word = ''.join(sorted(list(completed_pos.keys()), key=lambda l, l_pos=completed_pos: l_pos[l]))
    return guessed_word, guessed_word == word

'''
for word in word_list:
    guessed, correct = get_guess(word)
    print(guessed)
    print(correct)
'''
letter_pos, letters_unknown =  get_starting_info(WORD)
guessed_word = AI().get_best_guess(letter_pos, letters_unknown)
print(guessed_word, file_out=False)
print(guessed_word == WORD, file_out=False)

'''
for word in word_list:
    if len(set(word)) != 5:
        continue
    print(word)
    letter_pos, letters_unknown = get_starting_info(word)
    get_best_guess(letter_pos, letters_unknown)
    print(letter_pos, end='\n\n')
'''

if print_file is not None:
    print_file.close()