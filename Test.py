import numpy as np
import csv
from IPython.display import clear_output
from time import sleep
import random
import os
import pandas as pd
import matplotlib.pyplot as plt
import math
import Wordle_functions as wrdl
from timeit import default_timer as timer
from alive_progress import alive_bar, alive_it, config_handler
config_handler.set_global(force_tty=True, bar = "classic2", spinner = "classic", title='Playing Wordle intensively')

#Importing solutions and allowed words to lists
csv_reader = csv.reader(open('solutions.csv', 'r'))
solutions = list(csv_reader)[0] #contains all possible solutions

csv_reader = csv.reader(open('allowed_words.csv', 'r'))
allowed_words = list(csv_reader)[0] #contains allowed words beside solutions

all_allowed = allowed_words + solutions

solutions_EI = pd.read_csv('solutions_E[I].csv', header=0, index_col=0).squeeze("columns").to_dict()
allowed_EI = pd.read_csv('allowed_words_E[I].csv', header=0, index_col=0).squeeze("columns").to_dict()
all_allowed_EI = {**allowed_EI, **solutions_EI}


#Testing filter_words function
solution = "grade"
guess = "cigar"
answer = wrdl.wordle_reply(solution, guess)
print(answer)

reduced_list = wrdl.filter_words(guess, answer, all_allowed)
print(f"Original solution space: {len(all_allowed)}. Now: {len(reduced_list)}. Reduced list by {1-(len(reduced_list)/len(all_allowed)):.2%}")