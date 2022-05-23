import csv
import random
# import math
import inquirer

# import numpy as np
# import matplotlib.pyplot as plt
import Wordle_functions as wrdl
import Wordle_algo as algo

# from time import sleep
# from scipy.special import expit #sigmoid function


# Importing solutions and allowed words to lists
csv_reader = csv.reader(open('solutions.csv', 'r'))
solutions = list(csv_reader)[0]  # contains all possible solutions

csv_reader = csv.reader(open('allowed_words.csv', 'r'))
allowed_words = list(csv_reader)[0]  # contains allowed words beside solutions

all_allowed = allowed_words + solutions

possible_algorithms = [
    inquirer.List('algorithm',
                  message="Which algorithm to run",
                  choices=['Algorithm mark 1', "Algorithm mark 2", "Algorithm mark 3", "Algorithm mark 4"],
                  )
]
options = [
    inquirer.Checkbox('options',
                      message="Which options",
                      choices=['Verbose', "Manual", "Progress bar", "Minimize guesses"],
                      )
]
known_solution = [
    inquirer.List('solution',
                  message="What's the solution?",
                  choices=['unknown', "specify", "random", "automatic"],
                  )
]
solution = [
    inquirer.Text('solutions',
                  message="What's the solution word?")
]
nrsolutions = [
    inquirer.Text('solutions',
                  message="How many solutions? Max 2309")
]

answers = inquirer.prompt(possible_algorithms)
answers.update(inquirer.prompt(options))
answers.update(inquirer.prompt(known_solution))
if "specify" in answers["solution"]:
    # solutions = [input("Please enter a solution\n").lower()]
    answers.update(inquirer.prompt(solution))
    solutions = [answers["solutions"]]

    if len(solutions[0]) != 5: raise Exception("input needs to be 5 characters")
elif "random" in answers["solution"]:
    solutions = random.sample(solutions, len(solutions))
elif "automatic" in answers["solution"]:
    answers.update(inquirer.prompt(nrsolutions))
    solutions = solutions[0:int(answers["solutions"])]
else:
    solutions = ["Manual"]

manual = "Manual" in answers["options"]
verbose = "Verbose" in answers["options"]
bar = "Progress bar" in answers["options"]
if "Minimize guesses" in answers["options"]:
    custom_score = (-0.012405539570697632, 0.3642899622411526, 1.1890485932345454)
else:
    custom_score = (0, 0, 0)

if answers["algorithm"][-1] == "1":
    taken_tries = algo.wordle_algorithm_1(solutions=solutions, verbose=verbose, bar=bar, allowed_words=all_allowed)

if answers["algorithm"][-1] == "2":
    taken_tries = algo.wordle_algorithm_2(manual=manual, bar=bar, solutions=solutions, verbose=verbose,
                                          allowed_words=all_allowed)

if answers["algorithm"][-1] in ["3", "4"]:
    filename = input("Which filename?\n")
    print("\nLoading data from previous games")
    entropy_db = wrdl.load_entropy_db(filename)
    print(f"{len(entropy_db)} hashes imported\n")

if answers["algorithm"][-1] == "3":
    # loading word frequency dataset and creating dictionary of word frequency for all allowed words
    uniform_freq_map = {word: 1 for word in all_allowed}

    # running algo
    history = algo.wordle_algorithm_4(solutions=solutions,
                                      allowed_words=all_allowed,
                                      entropy_db=entropy_db,
                                      freq_map=uniform_freq_map,
                                      verbose=verbose,
                                      manual=manual,
                                      bar=bar,
                                      custom_score=(0, 0, 0))

if answers["algorithm"][-1] == "4":
    # loading word frequency dataset and creating dictionary of word frequency for all allowed words
    with open('unigram_freq.csv', 'r') as x:
        csv_reader = csv.reader(x)
        word_frequency_dict = list(csv_reader)

    del word_frequency_dict[0]  # delete headers
    word_frequency_dict = [(i, int(j)) for i, j in word_frequency_dict]
    total = sum(j for i, j in word_frequency_dict)
    word_frequency_dict = dict((i, j / total) for i, j in word_frequency_dict)

    all_allowed_freq = {}
    mini = min(word_frequency_dict.values())

    for word in all_allowed:
        if word in word_frequency_dict:
            all_allowed_freq[word] = word_frequency_dict[word]
        else:
            all_allowed_freq[word] = mini
    # applying sigmoid functions
    all_allowed_freq_sigmoid = algo.apply_sigmoid(all_allowed_freq, 10, -0.5)

    # running algo
    history = algo.wordle_algorithm_4(solutions=solutions,
                                      allowed_words=all_allowed,
                                      entropy_db=entropy_db,
                                      freq_map=all_allowed_freq_sigmoid,
                                      verbose=verbose,
                                      manual=manual,
                                      bar=bar,
                                      custom_score=custom_score)

try:
    tries = sum(i[-1][0] for i in list(history.values()))
    invalid = [i[-1][0] for i in list(history.values()) if i[-1][0] > 6]
    print(f"Average number of tries:\t{tries / len(history):.4}")
    print(f"Number of losses:\t\t{len(invalid)} = {len(invalid) / len(history):.2%}")
except:
    invalid_guesses = [x for x in taken_tries if x > 6]
    print(f"Average number of tries:\t{sum(taken_tries) / len(taken_tries):.2}")
    print(f"Number of losses:\t\t{len(invalid_guesses)} = {len(invalid_guesses) / len(taken_tries):.2%}")
