import csv
csv_reader = csv.reader(open('solutions.csv', 'r'))
solutions = list(csv_reader)[0]

csv_reader = csv.reader(open('allowed_words.csv', 'r'))
allowed_words = list(csv_reader)[0]

guess = input().lower()
if guess not in allowed_words:
            print("Guess not in allowed words")
else: print("success")
