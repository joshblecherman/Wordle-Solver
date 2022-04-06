# Wordle-Solver
Wordle solver/simulator

wordle_logic.py - a library I created to handle typical wordle logic such as narrowing down the field of words possible after a given guess, and then updating that field of words with future guess. Users interact with this library only through the LetterGroup class and the following functions: 
guess(**String**, **String**) 
get_guess_colors(**LetterGroup**) 
get_words(**LetterGroup = None**)

wordle_sim.py - a program that utilized the wordle_logic.py library to create a wordle simulator and a worldle solver 

