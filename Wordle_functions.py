import math
import pickle
import bz2
import numpy as np


def wordle_reply(solution, input):
    """
    Wordle game

        Args:
            solution (str):     5-Letter solution word
            input (str):        5-Letter input to be evaluated

        Returns:
            output (list):      List of 5 integers in Wordle logi
                2 = green:          letter placed correctly
                1 = yellow:         letter in the word but in wrong place
                0 = grey:           character not in word
    """
    if len(input) != 5:
        raise Exception("input needs to be 5 characters")
    output = [0] * 5
    solution = list(solution)
    input = list(input)

    # Check correctly placed chars
    for i in range(0, 5):
        if input[i] == solution[i]:
            output[i] = 2
            solution[i] = 0
            input[i] = False

    # Check incorrectly placed chars
    for i in range(0, 5):
        if input[i]:
            if input[i] in solution:
                output[i] = 1
                solution[solution.index(input[i])] = 0

    return output


def wordle_print(reply):
    # reply either [0, 0, 0, 0, 0]
    # or "00000"

    if type(reply) == str:
        reply = [int(d) for d in str(reply)]

    output_str = ""
    for element in reply:
        if element == 0:
            output_str += "⬜"
        elif element == 1:
            output_str += "🟨"
        elif element == 2:
            output_str += "🟩"
    return output_str


def filter_words(guess, answer, allowed_words):
    """
    Filters solution space from received information

        Args:
            guess (str):            The guess for which reply was received (e.g. "hello")
            answer(list):           List of int, e.g. [1, 2, 0, 2, 2] = 🟨🟩⬜🟩🟩
            allowed_words (list):   List of strings with allowed words. This list will be filtered
            

        Returns:
            allowed_words (list):    List of possible solutions after filtering out impossible words.
    """

    letter_count = {}

    # letter in word at correct place. Rejects all words where the letter is not in that position
    # Example: guess: moose, solution: bones -> all words without o at second position are rejected
    if 2 in answer:
        for i in range(5):
            letter = guess[i]
            if answer[i] == 2:
                allowed_words = list(filter(lambda x: x.startswith(letter, i), allowed_words))
                if letter not in letter_count:
                    letter_count[letter] = 1
                else:
                    letter_count[letter] += 1

    # letter in word at wrong place
    # Example: guess: sissy, solution: bones ->
    # all words with s at position 1 are rejected
    # all words that don't have an s are rejected
    if 1 in answer:
        for i in range(5):
            letter = guess[i]

            if answer[i] == 1:
                allowed_words = list(filter(lambda x: not x.startswith(letter, i),
                                            allowed_words))  # filters all words that have that char at that pos
                allowed_words = [k for k in allowed_words if
                                 letter in k]  # filters remaining list to force letter to be in word
                if letter not in letter_count:
                    letter_count[letter] = 1
                else:
                    letter_count[letter] += 1

    # letter not in word
    # Example: guess: sissy, solution: bones ->
    # all words with y are rejected
    # although reply for letter s at position 3 is 0, only words with s at position 3 are rejected, because it must be in the word somewhere
    if 0 in answer:
        for i in range(5):
            letter = guess[i]
            if answer[i] == 0:
                if not letter in letter_count:
                    allowed_words = [k for k in allowed_words if
                                     not letter in k]  # filter all words that have that letter
                else:
                    allowed_words = list(filter(lambda x: not x.startswith(letter, i),
                                                allowed_words))  # filters all words that have that char at that pos

    # letters not often enough in word
    for letter in letter_count:
        allowed_words = [k for k in allowed_words if k.count(letter) >= letter_count[letter]]

    # letters too often in word
    # Example: guess = "sissy", reply = [0,0,0,2,0]: "frass" needs to be filtered out
    for letter in letter_count:
        for i in range(6 - 1):
            for j in range(i + 1, 6 - 1):
                if guess[i] == guess[j] and guess[i] == letter:
                    if (answer[i] >= 1 and answer[j] == 0) or (answer[j] == 2 and answer[i] == 0):
                        allowed_words = [k for k in allowed_words if k.count(letter) == letter_count[letter]]

    return allowed_words


def wordle_reply_generator():
    """
    Generates reply_map with all possible wordl replies. Example reply: [1, 2, 0, 2, 2]           

        Returns:
            reply_map (list):   list of list of all possible wordl replies
    """
    reply_map = []
    for a in range(0, 22223):
        sub_list = [int(d) for d in "{:05d}".format(a)]
        reply_map.append(sub_list)

    for number in range(3, 10):
        reply_map = [k for k in reply_map if not number in k]
    return reply_map


def guess_probability_map(guess, word_list, freq_map, reply_map=wordle_reply_generator(), ):
    """
    Calculates how likely each wordle reply (e.g. [0 0 1 0 0]) is for a given guess,
    word_list (i.e. possible solutions) and reply_map (i.e. possible replies)

        Args:
            guess (str):        The guessed word
            word_list (list):   Possible solutions
            reply_map (list):   Possible replies. Will be filtered for invalid replies
            freq_map (dict):    Dictionary of words (key) and frequency (value)

        Returns:
            prob_list (list):   list of tuples with replies and probability of that reply
    """

    prob_list = []
    check_replies = False
    # if not freq_map: 
    #     freq_map = {k: (1/len(word_list)) for k in word_list}
    # else:
    #     total = sum(freq_map.values())
    #     freq_map = {k: (v/total) for (k, v) in freq_map.items()}

    if len(freq_map) < len(word_list) or round(sum(freq_map.values()), 10) != 1:
        raise Exception(f"something is wrong with freq_map {len(freq_map) - len(word_list)}\t{sum(freq_map.values())}")

    for c in guess:
        if guess.count(c) > 0:
            check_replies = True
            break

    for reply in reply_map:
        # check if reply makes sense -> e.g. for word sissy a reply [0 0 1 0 0] doesnt make sense
        # because if s is in word it would only be [1 0 0 0 0]/[2 0 0 0 0]/[0 0 0 2 0]/[1 0 0 2 0] etc.
        # In other words, it checkes if a letter in guess is twice and if yes it 
        if check_replies:
            invalid_reply = False
            for i in range(5):
                for j in range(i + 1, 5):
                    if guess[i] == guess[j]:
                        if reply[j] == 1 and reply[i] == 0:
                            invalid_reply = True

            if invalid_reply:
                continue

        # create prob_list
        matches = filter_words(guess, reply, allowed_words=word_list)
        matches_freq = [freq_map[x] for x in matches]
        prob = sum(matches_freq)

        if prob != 0:
            prob_list.append((reply, prob))

    return prob_list


def expected_entropy_from_map(probability_map):
    """
    Calculates expected entropy from a list of probabilities

        Args:
            probability_map (list): list of tuples with replies and probability of that reply

        Returns:
            e (float):              expected entropy E[I] in bits
    """

    if round(sum(row[1] for row in probability_map), 5) != 1:
        # makes sure that all probabilities sum up to 1
        raise Exception(f"What kind of probability map is that?! {round(sum(probability_map), 5)}")


def expected_entropy_from_map(probability_map):
    e = 0.0
    for p in probability_map:
        e += p[1] * math.log2(1 / p[1])

    return e


def expected_entropy_from_word(guess, word_list, reply_map=wordle_reply_generator(), freq_map={}):
    """
    Calculates how likely each wordle reply (e.g. [0 0 1 0 0]) is for a given guess,
    word_list (i.e. possible solutions) and reply_map (i.e. possible replies) and then
    calculates the expected entropy for that guess

        Args:
            guess (str):        The guessed word
            word_list (list):   Possible solutions
            reply_map (list):   Possible replies. Will be filtered for invalid replies
            freq_map (dict):    Dictionary of words (key) and frequency (value)

        Returns:
            e (float):          expected entropy E[I] in bits
    """
    if not freq_map:
        freq_map_standardised = {k: (1 / len(word_list)) for k in word_list}
    elif len(freq_map) != len(reply_map):
        freq_map_standardised = standardize_freq_map(freq_map, word_list)

    prob = guess_probability_map(guess, word_list, freq_map_standardised, reply_map=reply_map)
    e = expected_entropy_from_map(prob)
    return e


def standardize_freq_map(freq_map, word_list):
    """
    Standardizes a freq_map (dict) given a word list. Sum of freq_map will be set to 1
    and freq of words not included in word_list is set to 0.0

        Args:
            freq_map (dict):                Dictionary of words (key) and frequency (value)
            word_list (list):               Possible solutions

        Returns:
            freq_map_standardised (dict):   Standardized dictionary of words (key) and frequency (value)
    """
    freq_map_standardised = {k: v for (k, v) in freq_map.items()}
    for k in freq_map_standardised.keys():
        if k not in word_list: freq_map_standardised[k] = 0.0

    total = sum(freq_map_standardised.values())
    freq_map_standardised = {k: (v / total) for (k, v) in freq_map_standardised.items()}

    return freq_map_standardised


def entropy_from_distribution(freq_map, word_list):
    """
    Calculates the entropy / information in a distribution of words given their frequency

        Args:
            freq_map (dict):                Dictionary of words (key) and frequency (value)
            word_list (list):               Possible solutions

        Returns:
            freq_map_standardised (dict):   Standardized dictionary of words (key) and frequency (value)
    """
    inf = standardize_freq_map(freq_map, word_list)
    inf = [p * math.log2(1 / p) for p in inf.values() if p != 0]
    inf = sum(inf)

    return inf


def save_entropy_db(entropy_db, filename, n=30):
    """
    Saves entropy_db to pickled databases in multiple chunks

        Args:
            n (int):            Number of chunks
            entropy_db (dict):  The entropy_db dictionary
    """
    # filename = str(input("What filename to append to? e.g. entropy_db "))
    # try: 
    #     write = load_entropy_db(filename)
    #     write.update(entropy_db)
    # except:
    write = entropy_db
    #     pass
    lists = [{} for _ in range(n)]
    chunked_data = [[k, v] for k, v in write.items()]
    chunked_data = np.array_split(chunked_data, n)
    filename = str(input("What filename? e.g. entropy_db "))

    for i in range(n):
        for key, value in chunked_data[i]:
            lists[i][key] = value

    for i in range(n):
        with bz2.BZ2File(f'entropy database/{filename}_{str(i)}.pkl', 'wb') as x:
            print(f"Saving database {i + 1}/{n}")
            pickle.dump(lists[i], x)


def load_entropy_db(filename, n=30):
    """
    Loads entropy_db from multiple chunked files

        Args:
            n (int):            Number of chunks

        Returns:
            entropy_db (dict):  The entropy_db dictionary
    """
    entropy_db = {}
    #    filename = str(input("What filename? e.g. entropy_db "))

    for i in range(n):
        with bz2.BZ2File(f'entropy database/{filename}_{str(i)}.pkl', 'rb') as x:
            print(f"Loading database {i + 1}/{n}")
            entropy_db.update(pickle.load(x))

    return entropy_db


"""
Generate stable hashes for Python data objects.
Contains no business logic.
The hashes should be stable across interpreter implementations and versions.
Supports dataclass instances, datetimes, and JSON-serializable objects.
Empty dataclass fields are ignored, to allow adding new fields without
the hash changing. Empty means one of: None, '', (), [], or {}.
The dataclass type is ignored: two instances of different types
will have the same hash if they have the same attribute/value pairs.
"""
import dataclasses
import datetime
import hashlib
import json
from collections.abc import Collection
from typing import Any
from typing import Dict

# Implemented for https://github.com/lemon24/reader/issues/179


# The first byte of the hash contains its version,
# to allow upgrading the implementation without changing existing hashes.
# (In practice, it's likely we'll just let the hash change and update
# the affected objects again; nevertheless, it's good to have the option.)
#
# A previous version recommended using a check_hash(thing, hash) -> bool
# function instead of direct equality checking; it was removed because
# it did not allow objects to cache the hash.

_VERSION = 0
_EXCLUDE = '_hash_exclude_'


def get_hash(thing: object) -> bytes:
    prefix = _VERSION.to_bytes(1, 'big')
    digest = hashlib.md5(_json_dumps(thing).encode('utf-8')).digest()
    return prefix + digest[:-1]


def _json_dumps(thing: object) -> str:
    return json.dumps(
        thing,
        default=_json_default,
        # force formatting-related options to known values
        ensure_ascii=False,
        sort_keys=True,
        indent=None,
        separators=(',', ':'),
    )


def _json_default(thing: object) -> Any:
    try:
        return _dataclass_dict(thing)
    except TypeError:
        pass
    if isinstance(thing, datetime.datetime):
        return thing.isoformat(timespec='microseconds')
    raise TypeError(f"Object of type {type(thing).__name__} is not JSON serializable")


def _dataclass_dict(thing: object) -> Dict[str, Any]:
    # we could have used dataclasses.asdict()
    # with a dict_factory that drops empty values,
    # but asdict() is recursive and we need to intercept and check
    # the _hash_exclude_ of nested dataclasses;
    # this way, json.dumps() does the recursion instead of asdict()

    # raises TypeError for non-dataclasses
    fields = dataclasses.fields(thing)
    # ... but doesn't for dataclass *types*
    if isinstance(thing, type):
        raise TypeError("got type, expected instance")

    exclude = getattr(thing, _EXCLUDE, ())

    rv = {}
    for field in fields:
        if field.name in exclude:
            continue

        value = getattr(thing, field.name)
        if value is None or not value and isinstance(value, Collection):
            continue

        rv[field.name] = value

    return rv
