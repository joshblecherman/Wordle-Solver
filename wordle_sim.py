import wordle_logic as wl
from random import choice

answer = choice(wl.get_words())




def get_user_guess():
    guess = input("Enter a guess: ")
    while len(guess) != 5 or len([let for let in guess if 97 <= ord(let) <= 122]) != 5:
        print("invalid input")
        guess = input("Enter a guess: ")
    return guess

def get_inputted_colors():
    word = input("what word did you input? ")
    colors = input("Enter the result of your guess (Example: BGYBB) ")
    return word, list(colors)


if __name__ == "__main__":

    mode = input("""
        Wordle Sim: 1 
        Wordle Solve: 2
    """)

    mode = int(mode)

    if mode == 1:
        lg = wl.LetterGroup()
        while len(wl.get_words(lg)) > 1:
            new_data = wl.guess(get_user_guess(), answer)
            print(wl.get_guess_colors(new_data))
            lg.update(new_data)

            stuck = input("Are you stuck? (y/n)")

            if stuck == "y":
                print(wl.get_words(lg))

        print(wl.get_words(lg)[0])

    if mode == 2:
        lg = wl.LetterGroup(from_colors=get_inputted_colors())

        while len(wl.get_words(lg)) > 1:
            stuck = input("Are you stuck? (y/n)")
            if stuck == "y":
                print(wl.get_words(lg))

            new_lg = wl.LetterGroup(from_colors=get_inputted_colors())
            lg.update(new_lg)

        print(wl.get_words(lg)[0])




