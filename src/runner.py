#import pygame

from wordle import Wordle, WordleAI

game = Wordle()
ai = WordleAI(game)

def give_clues(word: str, guess: str):
    clue = {
        'word': guess,
        'clues': ['' for i in range(5)]
    }
    word_letter_counts = {}
    guess_letter_counts = {}
    for letter in set(word):
        word_letter_counts[letter] = word.count(letter)
    for letter in set(guess):
        guess_letter_counts[letter] = guess.count(letter)
    
    green_counts = {}
    for i in range(len(guess)):
        if guess[i] == word[i]:
            clue['clues'][i] = 'Green'
            green_counts[guess[i]] = 1
        elif guess[i] in word and guess[i] not in green_counts:
            clue['clues'][i] = 'Yellow'
        elif guess[i] not in word:
            clue['clues'][i] = 'Gray'
        elif guess[i] in word and guess_letter_counts[guess[i]] > word_letter_counts[guess[i]]:
            clue['clues'][i] = 'Gray'
        
    return clue

crateLions = True
word = 'table'
# guesses = acorn, plush, deity
if crateLions:
    ai.add_guess(give_clues(word, 'crate'))
    ai.add_guess(give_clues(word, 'lions'))
    ai.add_guess(give_clues(word, 'dumpy'))
    ai.add_guess(give_clues(word, 'blank'))
else:
    ai.add_guess(give_clues(word, 'acorn'))
    ai.add_guess(give_clues(word, 'plush'))
    ai.add_guess(give_clues(word, 'deity'))

#ai.add_guess(give_clues(word, 'crumb'))

ai.share_knowledge()
#print(ai.solution_consistent(ai.sentences[0].letter_pos))
aiGuess = ai.get_best_guess()

print(f'word was: {word}')
print(f'AI guessed: {aiGuess}')