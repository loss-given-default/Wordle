invalid_reply = False
guess = "sissy"
reply = [1, 0, 0, 0, 0]

for i in range(6-1):
    #count = 1
    for j in range(i+1, 6-1):
        a = guess[i]
        b = guess[j]
        if a == b:
            #count += 1
            if reply[j] == 1 and reply[i] == 0:
                invalid_reply = True
invalid_reply