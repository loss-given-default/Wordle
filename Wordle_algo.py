import random
import math
import inquirer
import os

import numpy as np
import matplotlib.pyplot as plt
import Wordle_functions as wrdl

from time import sleep
from alive_progress import alive_it, config_handler
from scipy.special import expit #sigmoid function

config_handler.set_global(force_tty=True, bar = "classic2", spinner = "classic", title='Playing Wordle intensively')

def clearConsole():
    command = 'clear'
    if os.name in ('nt', 'dos'):  # If Machine is running on Windows, use cls
        command = 'cls'
    os.system(command)


### Algorithm mark 1
#takes around 60 seconds to run
def wordle_algorithm_1(solutions = None, allowed_words = None, max_tries = 12974, manual = False, verbose = False, bar = False):
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

    if bar: bar = alive_it(solutions)
    else: bar = solutions

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
        taken_tries.append(i+1)
        #clear_output(wait=True)
    return taken_tries


### Algorithm mark 2
def wordle_algorithm_2(solutions = None, allowed_words = None, max_tries = 12974, manual = False, bar = True, verbose = False):
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

    if bar: bar = alive_it(solutions)
    else: bar = solutions

    for s in bar:
        guess = random.choice(allowed_words) #initial guess
        reduced_list = allowed_words
        if verbose: print(s)
        for i in range(max_tries): #reduces list over iterations
            if manual:
                print(f"Try: {guess}")
                sleep(1)
                reply = [int(item) for item in input("Wordl reply e.g. 0 2 1 0 0").split()]
                reduced_list = wrdl.filter_words(guess, reply, allowed_words = reduced_list)
                print(wrdl.wordle_print(reply), guess, f"{len(reduced_list)} words")
            else:
                reply = wrdl.wordle_reply(s, guess)
                reduced_list = wrdl.filter_words(guess, reply, allowed_words = reduced_list)
                inf = -math.log2(1/len(reduced_list))
                if verbose: print(wrdl.wordle_print(reply), guess, f"{len(reduced_list)} words\tI: {inf:.2}")

            guess = random.choice(reduced_list)

            if sum(reply) == 10:
                break
        taken_tries.append(i+1)
        #clear_output(wait=True)
    return taken_tries



def apply_sigmoid(data_dict, multiplier = 10, summand = -0.5):
    #transform to list
    values = [0, 0]
    values[0] = list(data_dict.keys())
    values[1] = list(data_dict.values())

    #log them
    values[1] = np.log(values[1])
    #standardize them
    values[1] /= np.std(values[1])
    values[1] -= np.mean(values[1])
    #adjust them
    values[1] += summand
    values[1] *= multiplier
    #sigmoid them
    values[1] = expit(values[1])

    #transform back to dict
    newD = dict(zip(values[0], values[1]))

    return newD




def wordle_algorithm_4(solutions = None, allowed_words = None, \
    max_tries = 12974, manual = False, verbose = False, entropy_db = None, \
    freq_map = None, bar = False):
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
            freq_map(dict):         xx TODO
            
        Returns:
            taken_tries (list):     list of int how many tries it took to solve for each solution
    """
    
    taken_tries = []
    reply = []
    print_queue = []
    len_db = len(entropy_db)

    if bar: bar = alive_it(solutions)
    else: bar = solutions

    for s in bar:
        hash_list = []
        hash_list = [sum(list(freq_map.values()))]
        allowed_words = sorted(allowed_words)
        reduced_list = allowed_words
        reduced_reply_map = wrdl.wordle_reply_generator()
        try: bar.title = f"-> Currently solving {s}"
        except: pass
        
        if manual or verbose: 
            inf = wrdl.standardize_freq_map(freq_map, reduced_list)
            inf = [p*math.log2(1/p) for (k, p) in inf.items()]
            inf = sum(inf)

            clearConsole()
            if manual: print_queue.append(f"I:{inf:.4}|{len(allowed_words)} possible solutions")
            else: print_queue.append(f"{s}|I:{inf:.4}|{solutions.index(s)+1/len(solutions):.2%}")
            for string in print_queue: print(string)
        for i in range(max_tries):
            cur_hash = wrdl.get_hash(str(hash_list))
            if len(reduced_list) == 1:
                guess = reduced_list[0]
                EI = 0
            else:
                if cur_hash in entropy_db:
                    entropies_list = entropy_db[cur_hash]
                else:   
                    #get all E[I] for reduced list
                    entropies_list = []         
                    tmp = len(allowed_words)
                    tmp2 = 1
                    #bar = alive_it(allowed_words)
                    for word in allowed_words:
                        try: bar.title = f"-> Calculating entropies {s} {tmp2}/{tmp}"
                        except: 
                            print(f"-> Calculating entropies {s} {tmp2}/{tmp}")
                            pass     
                        entropies_list.append(wrdl.expected_entropy_from_word(word, word_list = reduced_list, reply_map = reduced_reply_map, freq_map = freq_map))
                        tmp2 += 1
                    
                    entropy_db[cur_hash] = entropies_list
                entropies_dict_all = dict(zip(allowed_words, entropies_list))
                v = list(entropies_dict_all.values())
                k = list(entropies_dict_all.keys())
                cand = k[v.index(max(v))]   
                cand1 = [cand, entropies_dict_all[k[v.index(max(v))]]]

                entropies_dict_reduced = {k: entropies_dict_all[k] for k in reduced_list}
                v = list(entropies_dict_reduced.values())
                k = list(entropies_dict_reduced.keys())
                cand = k[v.index(max(v))]   
                cand2 = [cand, entropies_dict_reduced[k[v.index(max(v))]]]
           
                if cand1[1] > cand2[1]:
                    guess = cand1[0]
                    EI = float(cand1[1])
                else:
                    guess = cand2[0]
                    EI = float(cand2[1])
                
            if manual and EI != 0: 
                #Best guesses:
                #print_later = f"Guess: {cand2[0]}\tE[I]:{cand2[1]:.2f} bits"
                best_guesses = list(entropies_dict_all.items())
                best_guesses.sort(key=lambda x:x[1], reverse = True)

                print_later = ["", "", ""]
                i = 0
                for word in best_guesses:
                    if word[0] in reduced_list:
                        print_later[i] = f"{word[0]} E[I]:{word[1]:.2f} bits"
                        i += 1
                    if i == 3: break

                possible_guesses = [
                    inquirer.List('guess',
                                        message="Choose your guess!",
                                        choices=[
                                            f"{best_guesses[0][0]} E[I]:{best_guesses[0][1]:.2f} bits", 
                                            f"{best_guesses[2][0]} E[I]:{best_guesses[2][1]:.2f} bits", 
                                            f"{best_guesses[1][0]} E[I]:{best_guesses[1][1]:.2f} bits", 
                                            f"{best_guesses[3][0]} E[I]:{best_guesses[3][1]:.2f} bits",
                                            f"{best_guesses[4][0]} E[I]:{best_guesses[4][1]:.2f} bits",
                                            "--------------------",
                                            print_later[0],
                                            print_later[1],
                                            print_later[2],
                                            ],
                                        )
                    ]

                guess = inquirer.prompt(possible_guesses)["guess"][:5]
                try: EI = entropies_dict_all[guess]
                except:
                    guess = str(input()).lower()

                if EI == 0: #-> solution is known by algorithm
                    reply = [2, 2, 2, 2, 2]
                elif len(s) == 5: #-> solution was provided
                    reply = wrdl.wordle_reply(s, guess)
                else: #-> solution was not provided
                    reply = [int(item) for item in input("Wordl reply e.g. 0 2 1 0 0").split()]
                #clear_output(wait=True)
            else: reply = wrdl.wordle_reply(s, guess)
            hash_list.append((guess, reply))

            if sum(reply) == 10: 
                inf = math.log2(len(reduced_list)) #1/(1/x) = x #TODO Calculation incorrect for variable freq_map
                if manual or verbose: 
                    clearConsole()
                    print_queue.append(f"{wrdl.wordle_print(reply)} {guess} E[I]:{EI:.2f} bits I:{inf:.2f} bits ✔️")
                    for string in print_queue: print(string)
                break
        
            if manual or verbose:
                inf_before = wrdl.standardize_freq_map(freq_map, reduced_list)
                inf_before = sum([p*math.log2(1/p) for (k, p) in inf_before.items()])

                reduced_list = wrdl.filter_words(guess, reply, allowed_words = reduced_list)

                inf = wrdl.standardize_freq_map(freq_map, reduced_list)
                inf = [p*math.log2(1/p) for (k, p) in inf.items()]
                inf = inf_before - sum(inf)

                clearConsole()
                print_queue.append(f"{wrdl.wordle_print(reply)} {guess} E[I]:{EI:.2f} bits I:{inf:.2f} bits {len(reduced_list)} words")
                for string in print_queue: print(string)
                if 1 < len(reduced_list) < 16: print(reduced_list)

        taken_tries.append(i+1)        

    if len(entropy_db) > len_db:
        wrdl.save_entropy_db(entropy_db, "entropy_db")
        print(f"Pickled hashes updated - new len: {len(entropy_db)}")
    
    return taken_tries