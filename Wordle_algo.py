import random
import math
import inquirer
import os

import numpy as np
import Wordle_functions as wrdl

from time import sleep
from alive_progress import alive_it, config_handler
from scipy.special import expit  # sigmoid function
from IPython.display import clear_output

"""
Proudly coded by hand
Github with annotated functions and jupyter notebook on
https://github.com/loss-given-default/Wordle
"""

config_handler.set_global(force_tty=True, bar="classic2", spinner="classic", title='Playing Wordle intensively')


def clearConsole():
    command = 'clear'
    if os.name in ('nt', 'dos'):  # If Machine is running on Windows, use cls
        command = 'cls'
    os.system(command)


### Algorithm mark 1
def wordle_algorithm_1(solutions=None, allowed_words=None, max_tries=12974, manual=False, verbose=False, bar=False):
    """
    Wordle algorithm mark 1

        Args:
            solutions (list):       List of solutions (str) to iterate over. Is ignored if manual == True
            allowed_words (list):   List of strings with allowed words
            max_tries (int):        Max number of tries before giving up
            manual(bool):           If true, it asks for input for reply
            

        Returns:
            taken_tries (list):     list of int how many tries it took to solve for each solution
    """

    taken_tries = []
    if manual: solutions = ["a"]

    if bar:
        bar = alive_it(solutions)
    else:
        bar = solutions

    for s in bar:
        guess = random.sample(allowed_words, len(allowed_words))
        for i in range(max_tries):
            if manual:
                print(f"Try: {guess[i]}")
                sleep(1)
                reply = [int(item) for item in input("Wordl reply e.g. 0 2 1 0 0").split()]
                print(wrdl.wordle_print(reply), guess[i])
            else:
                reply = wrdl.wordle_reply(s, guess[i])

            if verbose: print(wrdl.wordle_print(reply), "", guess[i])
            if sum(reply) == 10:
                break
        taken_tries.append(i + 1)
        # clear_output(wait=True)
    return taken_tries


### Algorithm mark 2
def wordle_algorithm_2(solutions=None, allowed_words=None, max_tries=12974, manual=False, bar=True, verbose=False):
    """
    Wordle algorithm mark 2: Makes use of the information from wordl reply by filtering out words
    that can't be the solution. Suggests random word from solution space that's left as next guess.

        Args:
            solutions (list):       List of solutions (str) to iterate over. Is ignored if manual == True
            allowed_words (list):   List of strings with allowed words
            max_tries (int):        Max number of tries before giving up
            manual(bool):           If true, it asks for input for reply
            

        Returns:
            taken_tries (list):     list of int how many tries it took to solve for each solution
    """

    taken_tries = []
    if manual: solutions = ["a"]

    if bar:
        bar = alive_it(solutions)
    else:
        bar = solutions

    for s in bar:
        guess = random.choice(allowed_words)  # initial guess
        reduced_list = allowed_words
        if verbose: print(s)
        for i in range(max_tries):  # reduces list over iterations
            if manual:
                print(f"Try: {guess}")
                sleep(1)
                reply = [int(item) for item in input("Wordl reply e.g. 0 2 1 0 0").split()]
                reduced_list = wrdl.filter_words(guess, reply, allowed_words=reduced_list)
                print(wrdl.wordle_print(reply), guess, f"{len(reduced_list)} words")
            else:
                reply = wrdl.wordle_reply(s, guess)
                reduced_list = wrdl.filter_words(guess, reply, allowed_words=reduced_list)
                inf = -math.log2(1 / len(reduced_list))
                if verbose: print(wrdl.wordle_print(reply), guess, f"{len(reduced_list)} words\tI: {inf:.2}")

            guess = random.choice(reduced_list)

            if sum(reply) == 10:
                break
        taken_tries.append(i + 1)
        # clear_output(wait=True)
    return taken_tries


def apply_sigmoid(data_dict, multiplier=10, summand=-0.5):
    # transform to list
    values = [0, 0]
    values[0] = list(data_dict.keys())
    values[1] = list(data_dict.values())

    # log them
    values[1] = np.log(values[1])
    # standardize them
    values[1] /= np.std(values[1])
    values[1] -= np.mean(values[1])
    # adjust them
    values[1] += summand
    values[1] *= multiplier
    # sigmoid them
    values[1] = expit(values[1])

    # transform back to dict
    newD = dict(zip(values[0], values[1]))

    return newD


### Algorithm 3, 4 & 4.5
def wordle_algorithm_4(solutions=None, allowed_words=None, \
                       max_tries=12974, manual=False, verbose=False, entropy_db=None, \
                       freq_map=None, bar=False, custom_score=(0, 0, 0), jup=False):
    """
    Wordle algorithm mark 4: Makes use of the information from wordl reply by filtering out words
    that can't be the solution. Suggests guess with highest expected entropy from reduced solution
    space as next guess. Takes word frequency into account.

        Args:
            solutions (list):       List of solutions (str) to iterate over. Is ignored if manual == True
            allowed_words (list):   List of strings with allowed words
            max_tries (int):        Max number of tries before giving up
            manual(bool):           If true, it asks for input for reply
            verbose(bool):          If true lots of stuff is printed
            entropy_db(dict):       Dictionary of hashes with entropy list
            freq_map(dict):         Dictionary of words (key) and frequency (value). Does not need to be standardized
            custom_score():         tuple of 3 parameters from np.polyfit to calculate expected number of guesses
            jup(bool):              Clears screen for verbose mode in jup
            
        Returns:
            taken_tries (list):     list of int how many tries it took to solve for each solution
    """

    taken_tries = {}
    reply = []
    score_list = [None] * len(allowed_words)
    len_db = len(entropy_db)
    allowed_words = sorted(allowed_words)
    reduced_reply_map_save = wrdl.wordle_reply_generator()
    inf_start = wrdl.entropy_from_distribution(freq_map, allowed_words)

    if bar:
        bar = alive_it(solutions)
    else:
        bar = solutions

    for s in bar:

        history = []
        print_queue = []
        hash_list = [sum(list(freq_map.values()))]
        reduced_list = allowed_words
        reduced_reply_map = reduced_reply_map_save
        inf = inf_start

        try:
            bar.title = f"-> Currently solving {s}"
        except:
            pass

        if manual or verbose:
            # clearConsole()
            if jup: clear_output(wait=True)
            if manual:
                print_queue.append(f"\t\t\t\tI:{inf:.3} bits {len(allowed_words)} words")
            else:
                print_queue.append(f"{s}\tI:{inf:.4}\t{(solutions.index(s) + 1) / len(solutions):.2%}")
            for string in print_queue: print(string)
        for i in range(max_tries):
            history.append((i + 1, inf))
            cur_hash = wrdl.get_hash(str(hash_list))
            if len(reduced_list) == 1:
                guess = reduced_list[0]
                EI = 0
            else:
                if cur_hash in entropy_db:
                    entropies_list_all = entropy_db[cur_hash]
                else:
                    # get all E[I] for reduced list
                    entropies_list = []
                    tmp = len(allowed_words)
                    tmp2 = 1
                    # bar = alive_it(allowed_words)
                    for word in allowed_words:
                        try:
                            bar.title = f"-> Calculating entropies {s} {tmp2}/{tmp}"
                        except:
                            print(f"-> Calculating entropies {s} {tmp2}/{tmp}")
                            pass
                        entropies_list.append(
                            wrdl.expected_entropy_from_word(word, word_list=reduced_list, reply_map=reduced_reply_map,
                                                            freq_map=freq_map))
                        tmp2 += 1

                    # Select best guess
                    best_freq_map = wrdl.standardize_freq_map(freq_map, reduced_list)
                    prob_db = [best_freq_map[g] for g in allowed_words]

                    entropies_list_all = list(zip(entropies_list, prob_db, allowed_words))
                    entropies_list_all = sorted(entropies_list_all, reverse=True)

                    entropy_db[cur_hash] = entropies_list_all  # TODO Check if it works

                for j in range(len(entropies_list_all)):
                    x, p, word = entropies_list_all[j]
                    x = inf - x  # Expected residual entropy of solution space after guessing word
                    a, b, c = custom_score  # parameters of polyfit regression (2 degrees)
                    if a == b == c == 0:
                        score = 0
                    else:
                        score = p * (i + 1) + (1 - p) * ((i + 1) + (a * pow(x, 2) + b * x + c))
                    score_list[j] = (round(-score, 10), round(inf - x, 10), p, word)
                score_list = sorted(score_list, reverse=True)

                guess = score_list[0][-1]
                EI = score_list[0][1]

            if manual and EI != 0:
                print_later = ["", "", ""]
                i = 0
                for word in score_list:
                    if word[-1] in reduced_list:
                        print_later[i] = f"{word[-1]} E[I]:{word[-3]:.2f} bits P: {word[-2]:.2%} S: {word[0]:.2f}"
                        i += 1
                    if i == 3: break

                possible_guesses = [
                    inquirer.List('guess',
                                  message="Choose your guess!",
                                  choices=[
                                      f"{score_list[0][-1]} E[I]:{score_list[0][-3]:.2f} bits P: {score_list[0][-2]:.2%} S: {score_list[0][0]:.2f}",
                                      f"{score_list[1][-1]} E[I]:{score_list[1][-3]:.2f} bits P: {score_list[1][-2]:.2%} S: {score_list[1][0]:.2f}",
                                      f"{score_list[2][-1]} E[I]:{score_list[2][-3]:.2f} bits P: {score_list[2][-2]:.2%} S: {score_list[2][0]:.2f}",
                                      f"{score_list[3][-1]} E[I]:{score_list[3][-3]:.2f} bits P: {score_list[3][-2]:.2%} S: {score_list[3][0]:.2f}",
                                      f"{score_list[4][-1]} E[I]:{score_list[4][-3]:.2f} bits P: {score_list[4][-2]:.2%} S: {score_list[4][0]:.2f}",
                                      "--------------------",
                                      print_later[0],
                                      print_later[1],
                                      print_later[2],
                                  ],
                                  )
                ]

                guess = inquirer.prompt(possible_guesses)["guess"][:5]
                try:
                    EI = [x[1] for x in score_list if x[3] == guess][0]
                except:
                    guess = str(input()).lower()
                    EI = [x[1] for x in score_list if x[3] == guess][0]

                if EI == 0:  # -> solution is known by algorithm
                    reply = [2, 2, 2, 2, 2]
                elif len(s) == 5:  # -> solution was provided
                    reply = wrdl.wordle_reply(s, guess)
                else:  # -> solution was not provided
                    reply = [int(item) for item in input("Wordl reply e.g. 0 2 1 0 0\n").split()]
            elif EI == 0:
                reply = [2, 2, 2, 2, 2]
            else:
                reply = wrdl.wordle_reply(s, guess)

            if sum(reply) == 10:
                if manual or verbose:
                    clearConsole()
                    if jup: clear_output(wait=True)
                    print_queue.append(f"{wrdl.wordle_print(reply)} {guess} E[I]:{EI:.2f} bits I:{inf:.2f} bits ✔️")
                    for string in print_queue: print(string)

                break

            hash_list.append((guess, reply))
            inf_before = inf
            reduced_list = wrdl.filter_words(guess, reply, allowed_words=reduced_list)
            inf = float(wrdl.entropy_from_distribution(freq_map, reduced_list))
            rec_inf = inf_before - inf

            if manual or verbose:
                clearConsole()
                if jup: clear_output(wait=True)
                print_queue.append(
                    f"{wrdl.wordle_print(reply)} {guess} E[I]:{EI:.2f} bits I:{rec_inf:.2f} bits {len(reduced_list)} words {inf:.3} bits left")
                for string in print_queue: print(string)
                if 1 < len(reduced_list) < 16: print(reduced_list)

        taken_tries[s] = history

    if len(entropy_db) > len_db:
        wrdl.save_entropy_db(entropy_db, "entropy_db")
        print(f"Pickled hashes updated - new len: {len(entropy_db)}")

    return taken_tries
