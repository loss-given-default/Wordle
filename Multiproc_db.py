import csv
import multiprocessing
import pickle

import Wordle_functions as wrdl

from multiprocessing import Pool
from alive_progress import alive_bar


def wordle_algorithm_4(solutions=None, allowed_words=None, \
                       entropy_db=None, \
                       freq_map=None):
    reply = []

    for s in solutions:
        hash_list = []
        allowed_words = sorted(allowed_words)
        reduced_list = allowed_words
        reduced_reply_map = wrdl.wordle_reply_generator()

        while True:
            cur_hash = str(hash_list)
            if len(reduced_list) == 1:
                guess = reduced_list[0]
            else:
                if cur_hash in entropy_db:
                    entropies_list = entropy_db[cur_hash]
                else:
                    # get all E[I] for reduced list
                    entropies_list = []
                    tmp = len(allowed_words)
                    tmp2 = 1
                    print(f"-> Calculating entropies for {s}, {len(reduced_list)} possible solutions")
                    for word in allowed_words:
                        # print(f"omfg it working\t{tmp2}/{tmp}\t{(tmp2/tmp):.2%}")
                        entropies_list.append(
                            wrdl.expected_entropy_from_word(word, word_list=reduced_list, reply_map=reduced_reply_map,
                                                            freq_map=freq_map))
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
                else:
                    guess = cand2[0]

            reply = wrdl.wordle_reply(s, guess)
            hash_list.append((guess, reply))

            if sum(reply) == 10:
                break

            reduced_list = wrdl.filter_words(guess, reply, allowed_words=reduced_list)
            print(wrdl.wordle_print(reply), guess, f"{len(reduced_list)} words")

    return entropy_db


# takes xx minutes to run
# entropy_db_freq = {}
# taken_tries = wordle_algorithm_4(solutions[:1], verbose = True)
# invalid_guesses = [x for x in taken_tries if x > 6]

# sleep(1)
# print(f"Average number of tries:\t{sum(taken_tries)/len(taken_tries):.4}")
# print(f"Number of losses:\t\t{len(invalid_guesses)} = {len(invalid_guesses)/len(taken_tries):.2%}")

def f(iteration):
    print(iteration)
    entropy_db_freq = wrdl.load_entropy_db("entropy_db_freq")

    # Importing solutions and allowed words to lists
    csv_reader = csv.reader(open('solutions.csv', 'r'))
    solutions = list(csv_reader)[0]  # contains all possible solutions
    csv_reader = csv.reader(open('allowed_words.csv', 'r'))
    allowed_words = list(csv_reader)[0]  # contains allowed words beside solutions
    all_allowed = allowed_words + solutions

    with open("all_allowed_freq_sigmoid.pkl", 'rb') as x:
        all_allowed_freq_sigmoid = pickle.load(x)

    solutions = [solutions[iteration]]

    entropy_db_freq = wordle_algorithm_4(solutions, allowed_words=all_allowed, entropy_db=entropy_db_freq,
                                         freq_map=all_allowed_freq_sigmoid)
    return entropy_db_freq


if __name__ == '__main__':
    print("Hi")
    entropy_db_freq = wrdl.load_entropy_db("entropy_db_freq")
    old_len = len(entropy_db_freq)
    print(f"old len: {old_len}")

    iterations = 2309
    # start worker processes
    with alive_bar(iterations) as bar:
        with Pool(processes=multiprocessing.cpu_count()) as pool:
            for i in pool.imap_unordered(f, range(iterations)):
                entropy_db_freq.update(i)
                bar()

    # saving highscore
    if len(entropy_db_freq) > old_len:
        wrdl.save_entropy_db(entropy_db_freq, "entropy_db_freq")
        print(f"Pickled hashes updated - new len: {len(entropy_db_freq)}")
