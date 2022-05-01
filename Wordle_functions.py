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

    #Check correctly placed chars
    for i in range(0, 5):
        if input[i] == solution[i]: 
            output[i] = 2
            solution[i] = 0
            input[i] = False


    #Check incorrectly placed chars
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
        if element == 0: output_str += "⬜"
        elif element == 1: output_str += "🟨"
        elif element == 2: output_str += "🟩"
    return output_str

def filter_words(guess, answer, allowed_words): 
    # !This function is not very efficient.
    # ?Can we improve this?
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

    #letter in word at correct place. Rejects all words where the letter is not in that position
    #Example: guess: moose, solution: bones -> all words without o at second position are rejected
    for i in range(5):
        letter = guess[i]
        if answer[i] == 2:
            allowed_words = list(filter(lambda x: x.startswith(letter, i), allowed_words))
            if letter not in letter_count:
                letter_count[letter] = 1
            else:
                letter_count[letter] += 1

    #letter in word at wrong place
    #Example: guess: sissy, solution: bones -> 
        #all words with s at position 1 are rejected
        #all words that don't have an s are rejected
    for i in range(5):
        letter = guess[i]

        if answer[i] == 1:
            allowed_words = list(filter(lambda x: not x.startswith(letter, i), allowed_words)) #filters all words that have that char at that pos
            allowed_words = [k for k in allowed_words if letter in k] #filters remaining list to force letter to be in word
            if letter not in letter_count:
                letter_count[letter] = 1
            else:
                letter_count[letter] += 1
        
    #letter not in word
    #Example: guess: sissy, solution: bones ->
        #all words with y are rejected
        #although reply for letter s at position 3 is 0, only words with s at position 3 are rejected, because it must be in the word somewhere
    for i in range(5):
        letter = guess[i]
        if answer[i] == 0:
            if not letter in letter_count:
                allowed_words = [k for k in allowed_words if not letter in k] #filter all words that have that letter
            else:
                allowed_words = list(filter(lambda x: not x.startswith(letter, i), allowed_words)) #filters all words that have that char at that pos

    #letters not often enough in word
    for letter in letter_count:
        allowed_words = [k for k in allowed_words if  k.count(letter) >= letter_count[letter]]

    #letters too often in word
    #Example: guess = "sissy", reply = [0,0,0,2,0]: "frass" needs to be filtered out
    for letter in letter_count:
        for i in range(6-1):
            for j in range(i+1, 6-1):
                if guess[i] == guess[j] and guess[i] == letter:
                    if (answer[i] >= 1 and answer[j] == 0) or (answer[j] == 2 and answer[i] == 0):
                        allowed_words = [k for k in allowed_words if  k.count(letter) == letter_count[letter]]

    return allowed_words


def wordle_reply_generator():
    #?dumbest way to create list of all possible replies but I cant think of a better way rn
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