
with open('./src/word_list.txt', 'r', encoding='utf-8') as f:
    word_list = [line.strip() for line in f.readlines()]

alph = 'abcdefghijklmnopqrstuvwxyz'

def get_locations():
    pos_counts = {char: [0 for _ in range(5)] for char in alph}
    pos_order = {char: list(range(5)) for char in alph}
    for word in word_list:
        for i, char in enumerate(word):
            pos_counts[char][i] += 1

    for char in alph:
        pos_order[char].sort(key=lambda x, c=char: pos_counts[c][x], reverse=True)
    return pos_order
