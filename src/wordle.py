from typing import Iterator, Union

def unique(seq):
    seen = []
    return not any(i in seen or seen.append(i) for i in seq)

class Wordle:
    def __init__(self):
        with open('./src/guess_list.txt', 'r', encoding='utf8') as f:
            self.guess_list = f.read().splitlines()


"""
{
    "word": [word],
    "clues": [
        [color],
        [color],
        [color],
        [color],
        [color],
    ]
}
"""

class Sentence:
    """
    Logical Sentence about a Wordle game
    A sentence consists of the information gained from a guess
    """
    def __init__(self, guess: dict[str]):
        self.word: str = guess['word']
        self.clues: list[str] = guess['clues']
        self.letters_unknown: set[str] = {chr(i) for i in range(97, 123)} # initialize set of letters to contain all letters in alphabet
        self.letters_in_word: set[str] = set()
        self.known_letters = ['' for _ in range(5)]
        self.letter_pos: dict[str, Union[int, list[int]]] = {}
        self.gather_info()

    def __eq__(self, other) -> bool:
        return self.letters_unknown == other.letters_unknown and self.clues == other.clues and self.word == other.word
    
    def __str__(self) -> str:
        return f"{self.word} {self.clues}"
    
    def gather_info(self):
        clues = self.clues
        word = self.word
        for i in range(len(clues)):
            clue = clues[i]
            char = word[i]
            if clue == "Green":
                self.known_letters[i] = char
                self.letters_in_word.add(char)
                self.letters_unknown.remove(char)
            elif clue == "Yellow":
                self.letters_unknown.remove(char)
                self.letters_in_word.add(char)
            elif clue == "Gray":
                self.letters_unknown.remove(char)
            else:
                raise ValueError("Invalid clue")
            if char in self.letters_in_word:
                if clue == "Green":
                    self.letter_pos[char] = i
                else:
                    self.letter_pos[char] = sorted(list(set(range(5)) - {i}))
    def add_info(self, other):
        self.letters_unknown.intersection_update(other.letters_unknown)
        self.letters_in_word.update(other.letters_in_word)
        
        for i in range(len(self.known_letters)):
            self_known = self.known_letters[i]
            other_known: str = other.known_letters[i]
            if self_known == '' and other_known != '':
                self.known_letters[i] = other_known
                self.letters_in_word.add(other_known)
                self.letters_unknown.discard(other_known)
        for char in other.letter_pos:
            if char not in self.letter_pos:
                self.letter_pos[char] = other.letter_pos[char]
            else:
                if isinstance(other.letter_pos[char], int):
                    self.letter_pos[char] = other.letter_pos[char]
                elif isinstance(self.letter_pos[char], int):
                    pass
                else:
                    self.letter_pos[char] = sorted(list(set(self.letter_pos[char]) & set(other.letter_pos[char])))
        if len(self.letter_pos) == 5:
            self.letters_unknown = set()
        self.update_letter_pos()
    def update_letter_pos(self):
        known_pos = []
        for letter in self.known_letters:
            if letter != '':
                known_pos.append(self.letter_pos[letter])
        found_letter_pos = False
        for char in self.letter_pos:
            if isinstance(self.letter_pos[char], int):
                pass
            else:
                self.letter_pos[char] = sorted(list(set(self.letter_pos[char]) - set(known_pos)))
                if len(self.letter_pos[char]) == 1: # if there is only one possible position, set it to that
                    pos: int = self.letter_pos[char][0]
                    self.letter_pos[char] = pos
                    self.known_letters[pos] = char
                    found_letter_pos = True
        if found_letter_pos:
            # if we've found a letter, update the letter_pos
            self.update_letter_pos()
                    

class WordleAI:
    def __init__(self, game: Wordle):
        self.sentences: list[Sentence] = []
        self.guesses: list[str] = []
        self.game = game
    
    def add_guess(self, guess: dict[str]):
        self.sentences.append(Sentence(guess))
        self.guesses.append(guess['word'])

    def share_knowledge(self):
        for sentence in self.sentences:
            for other_sentence in self.sentences:
                if sentence != other_sentence:
                    sentence.add_info(other_sentence)
                    other_sentence.add_info(sentence)
    
    def get_best_guess(self):
        self.share_knowledge()
        sentence = self.sentences[0]
        res = self.backtrack(sentence.letter_pos)
        if res is not None:
            if all(isinstance(pos, int) for pos in res.values()):
                return ''.join(sorted(list(res.keys()), key=lambda x: res[x]))
        return None

    def solution_complete(self, letter_pos: dict[str]):
        return all(isinstance(pos, int) for pos in letter_pos.values()) and len(letter_pos) == 5

    def solution_consistent(self, letter_pos: dict[str]):
        return unique([i for i in letter_pos.values() if isinstance(i, int)])

    def solution_is_valid(self, letter_pos: dict[str]):
        return all(isinstance(pos, int) for pos in letter_pos.values()) and ''.join(sorted(list(letter_pos.keys()), key=lambda x: letter_pos[x])) in self.game.guess_list

    def order_pos_values(self, letter_pos: dict[str], char):
        unknown_letter_pos = {char: pos for char, pos in letter_pos.items() if isinstance(pos, list) and len(pos) > 1}
        if char not in unknown_letter_pos:
            raise ValueError("letter not in letter_pos")
        pos_values = unknown_letter_pos[char]
        eliminations = {pos: 0 for pos in pos_values}
        other_chars = list(unknown_letter_pos.keys())
        for pos in pos_values:
            for other_char in other_chars:
                for other_pos in unknown_letter_pos[other_char]:
                    if other_pos == pos:
                        eliminations[pos] += 1
        return sorted(pos_values, key=lambda pos: eliminations[pos])

    def choose_unassigned_letter(self, letters: Iterator[str], all_possible_letters: Iterator[str]):
        try:
            return next(letters)
        except StopIteration:
            return next(all_possible_letters)

    def backtrack(self, letter_pos):
        if self.solution_complete(letter_pos):
            return letter_pos
        sentence = self.sentences[0]
        unknown_letter_pos = {char: pos for char, pos in letter_pos.items() if isinstance(pos, list) and len(pos) > 1}
        letters = iter(sorted(list(unknown_letter_pos.keys()), key=lambda char: len(unknown_letter_pos[char])))
        all_possible_letters = iter(list(sentence.letters_unknown))
        char = self.choose_unassigned_letter(letters, all_possible_letters)
        while True:
            if char in sentence.letters_in_word:
                pos_values = self.order_pos_values(letter_pos, char)
            else:
                pos_values = list({0, 1, 2, 3, 4} - set([pos for pos in letter_pos.values() if isinstance(pos, int)]))
            new_letter_pos = letter_pos.copy()
            for pos in pos_values:
                new_letter_pos[char] = pos
                if self.solution_consistent(new_letter_pos):
                    if len(new_letter_pos) == 5:
                        if self.solution_is_valid(new_letter_pos):
                            return new_letter_pos
                    result = self.backtrack(new_letter_pos)
                    if result is not None:
                        if self.solution_is_valid(result):
                            return result
                    new_letter_pos = letter_pos.copy()
            try:
                char = self.choose_unassigned_letter(letter_pos, all_possible_letters)
            except StopIteration:
                break
        return None