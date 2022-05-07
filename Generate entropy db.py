import pandas as pd
import csv
import Wordle_functions as wrdl
import pickle
from alive_progress import alive_bar, alive_it, config_handler
config_handler.set_global(force_tty=True, bar = "classic2", spinner = "classic", title='Playing Wordle intensively')

#Importing solutions and allowed words to lists
csv_reader = csv.reader(open('solutions.csv', 'r'))
solutions = list(csv_reader)[0] #contains all possible solutions
csv_reader = csv.reader(open('allowed_words.csv', 'r'))
allowed_words = list(csv_reader)[0] #contains allowed words beside solutions
all_allowed = allowed_words + solutions

#build dataframe with words & expected entropy and save as df
#for solutions
# entropies_all = []
# for word in alive_it(solutions):
#     entropies_all.append(wrdl.expected_entropy_from_word(word))

# df = pd.DataFrame(list(zip(solutions, entropies_all)), columns = ["Word", "E[I]"])
# df = df.sort_values(by=['E[I]'], ascending=False)
# df.to_csv('solutions_E[I].csv', index=False)

#for allowed_words (not all_allowed!)
entropies_all = []
for word in alive_it(allowed_words, force_tty=True, bar = "classic2", spinner = "loving"):
    entropies_all.append(wrdl.expected_entropy_from_word(word, all_allowed))

df = pd.DataFrame(list(zip(allowed_words, entropies_all)), columns = ["Word", "E[I]"])
df = df.sort_values(by=['E[I]'], ascending=False)
df.to_csv('allowed_words_E[I].csv', index=False)