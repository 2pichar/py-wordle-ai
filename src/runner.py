"Runner for Python Wordle AI"
from wordle import Wordle, WordleAI
#import pygame


def play_game():
    game = Wordle()
    game.word = 'focal'
    wordle_ai = WordleAI(game)

    for i in range(6):
        ai_guess = wordle_ai.get_best_guess()
        print(f"ai guessed '{ai_guess}'")
        if ai_guess is None:
            print("ai couldn't guess")
            print(f"the word was '{game.word}'")
            break
            return False, None
        elif game.is_solution(ai_guess):
            print(f"the word was '{ai_guess}'")
            print(f'ai won in {i+1} guesses')
            break
            return True, i+1
        else:
            clues = game.make_guess(ai_guess)
            wordle_ai.add_guess(clues)
            wordle_ai.share_knowledge()
    else:
        print('ai lost')
    #return False, None
"""
num_wins: int = 0
num_loss: int = 0
num_games: int = 100
total_guesses: int = 0
needed_5th_guess: int = 0
for _ in range(num_games):
    did_win, num_guesses = play_game()
    if did_win:
        num_wins += 1
        total_guesses += num_guesses
        if num_guesses > 4:
            needed_5th_guess += 1
    else:
        num_loss += 1
print(f'ai won {num_wins} times')
print(f'ai lost {num_loss} times')
print(f'ai win percentage: {num_wins/num_games*100}%')
print(f'ai average guesses: {round(total_guesses/num_wins, 2)}')
print(f'% of time ai needed 5th guess: {round(needed_5th_guess/num_wins*100, ndigits=2)}%')

# before: 45%, 53%
# after: 67%, 73%, 69%
"""
#play_game()

game = Wordle()
game.word = 'cabin'
wordle_ai = WordleAI(game)
for i in range(3):
    guess = wordle_ai.get_best_guess()
    wordle_ai.add_guess(game.make_guess(guess))
wordle_ai.share_knowledge()
print('')