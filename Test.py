import csv
import pickle
import random
import math

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import Wordle_functions as wrdl

from IPython.display import clear_output
from time import sleep
from alive_progress import alive_it, config_handler

config_handler.set_global(force_tty=True, bar = "classic2", spinner = "classic", title='Playing Wordle intensively')

#Importing solutions and allowed words to lists
csv_reader = csv.reader(open('solutions.csv', 'r'))
solutions = list(csv_reader)[0] #contains all possible solutions

csv_reader = csv.reader(open('allowed_words.csv', 'r'))
allowed_words = list(csv_reader)[0] #contains allowed words beside solutions

all_allowed = allowed_words + solutions

with open('entropy_db.pkl', 'rb') as x:
    entropy_db = pickle.load(x)

#takes xx seconds to run
def wordle_algorithm_3(solutions = solutions, allowed_words = all_allowed, \
    max_tries = len(all_allowed), manual = False, verbose = False, entropy_db = entropy_db):
    """
    Wordle algorithm mark 3: Makes use of the information from wordl reply by filtering out words
    that can't be the solution. Suggests guess with highest expected entropy from reduced solution
    space as next guess.

        Args:
            solutions (list):       List of solutions (str) to iterate over. Is ignored if manual == True
            allowed_words (list):   List of strings with allowed words
            max_tries (int):        Max number of tries before giving up
            manual(bool):           If true, it asks for input for reply
            verbose(bool):          If true lots of stuff is printed
            entropy_db(dict):       Dictionary of hashes with entropy list
            
        Returns:
            taken_tries (list):     list of int how many tries it took to solve for each solution
    """
    
    taken_tries = []
    reply = []
    len_db = len(entropy_db)
    if manual:
        solutions = ["a"]

    for s in alive_it(solutions):
        hash_list = []
        reduced_list = sorted(allowed_words)
        reduced_reply_map = wrdl.wordle_reply_generator()
        # if allowed_words == all_allowed:
        #     entropies_sorted = list(sorted(all_allowed_EI.items()))
        # else:
        #     entropies_sorted = list(sorted(solutions_EI.items()))
        # entropies_list = list(np.array(entropies_sorted)[:,1])  
        
        if verbose: print(s)
        for i in range(max_tries):
            cur_hash = hash(str(hash_list))
            if cur_hash in entropy_db:
                entropies_list = entropy_db[cur_hash]
            else:
                #reduce reply map if 2 is present:
                index_of_2s = np.where(np.array(reply) == 2)[0]
                for ind in index_of_2s:
                    reduced_reply_map = [x for x in reduced_reply_map if x[ind] == 2]        
                
                #get all E[I] for reduced list
                entropies_list = []
                for word in reduced_list:
                    entropies_list.append(wrdl.expected_entropy_from_word(word, word_list = reduced_list, reply_map = reduced_reply_map))
                
                entropy_db[cur_hash] = entropies_list

            guess = reduced_list[entropies_list.index(max(entropies_list))]
            EI = float(max(entropies_list))
            if manual: 
                print(f"Guess: {guess}\tE[I]:{EI:.2f} bits")
                sleep(2)
                reply = [int(item) for item in input("Wordl reply e.g. 0 2 1 0 0").split()]
            else: reply = wrdl.wordle_reply(s, guess)
            hash_list.append((guess, reply))

            if sum(reply) == 10: 
                inf = math.log2(len(reduced_list)) #1/(1/x) = x
                if manual or verbose: print(wrdl.wordle_print(reply), guess, f"E[I]:{EI:.2f} bits ", f"I:{inf:.2f} bits ", f"EPIC WIN!!!")
                break
        
            reduced_list_before = reduced_list
            reduced_list = wrdl.filter_words(guess, reply, allowed_words = reduced_list)
            p = len(reduced_list) / len(reduced_list_before)  
            inf = math.log2(1/p)
            if manual or verbose: print(wrdl.wordle_print(reply), guess, f"E[I]:{EI:.2f} bits ", f"I:{inf:.2f} bits ", f"{len(reduced_list)} words")
            

        taken_tries.append(i+1)
        if not manual: clear_output(wait=True)

    if len(entropy_db) > len_db and manual == False:
        with open('entropy_db.pkl', 'wb') as x:
            pickle.dump(entropy_db, x)
        print("Pickled hashes updated")
    
    return taken_tries





taken_tries = wordle_algorithm_3(solutions[:15], verbose = True)
invalid_guesses = [x for x in taken_tries if x > 6]

sleep(1)
print(f"Average number of tries: {sum(taken_tries)/len(taken_tries):.2}")
print(f"Number of losses:\t\t{len(invalid_guesses)} = {len(invalid_guesses)/len(solutions):.2%}")