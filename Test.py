def double(float):
    return float*2

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