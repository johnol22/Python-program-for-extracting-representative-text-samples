import numpy
import math
import csv
import os


# Line objects represent each line(sentence) of the original text. Each Line object contains a list of
# word lengths in that sentence.
class Line:
    def __init__(self, string):
        self.string = string

        self.word_lengths = []
        raw_split = string.split(' ')
        for item in raw_split:
            word_len = 0
            for char in item:
                if char.isalpha():
                    word_len += 1
            if word_len > 0:
                self.word_lengths.append(word_len)


# Extract objects represent each extract. Each Extract object contains a list of word lengths (for all sentences)
# and sentence lengths in that extract.
class Extract:
    def __init__(self, extract_number):
        self.extract_number = extract_number
        self.rank_number = 0
        self.lines = []  # Contains a list of Line objects
        self.word_lengths = []  # A list of numbers representing word lengths (in characters)
        self.sentence_lengths = []  # A list of numbers representing sentence lengths (in words)
        self.AWL_z_squared = 0  # The z-score for average word length
        self.ASL_z_squared = 0  # The z-score for average sentence length
        self.combined_z_score = 0

    def add_line(self, string):
        self.lines.append(string)

    def del_last_line(self):
        self.lines = self.lines[:-1]

    def calculate_totals(self):
        for line in self.lines:
            self.sentence_lengths.append(len(line.word_lengths))
            self.word_lengths += line.word_lengths

        # Calculating the z-score for average word length (AWL)
        sample_mean = numpy.mean(self.word_lengths)
        population_mean = numpy.mean(original_text.word_lengths)
        population_sd = numpy.std(original_text.word_lengths)
        sample_size = len(self.word_lengths)
        z_score = (sample_mean - population_mean) / (population_sd / math.sqrt(sample_size))
        self.AWL_z_squared = z_score ** 2

        # Calculating the z-score for average sentence length (ASL)
        sample_mean = numpy.mean(self.sentence_lengths)
        population_mean = numpy.mean(original_text.sentence_lengths)
        population_sd = numpy.std(original_text.sentence_lengths)
        sample_size = len(self.sentence_lengths)
        z_score = (sample_mean - population_mean) / (population_sd / math.sqrt(sample_size))
        self.ASL_z_squared = z_score ** 2

        # Combining the two z-scores
        self.combined_z_score = self.AWL_z_squared + self.ASL_z_squared

    def get_all_values(self):
        return [
            self.rank_number,
            self.extract_number,
            len(self.word_lengths),  # Number of words
            numpy.mean(self.word_lengths),  # Average word length (AWL)
            self.AWL_z_squared,  # Z-score squared (for AWL)
            numpy.mean(self.sentence_lengths),  # Average sentence length (ASL)
            self.ASL_z_squared,  # Z-score squared (for ASL)
            self.combined_z_score  # Combined z-score
        ]


# The length of sample needed (change here if you need a different length)
sample_length = 300

# Loads the original text from the file (change filename here if needed)
input_filename = "example_text.txt"
f = open(input_filename, "r")
text = f.read()

# Removes unwanted whitespace
text = " ".join(text.split())

# Splits the text by sentence. Note that a sentence is considered finished at a full stop. If a full stop
# occurs at any other point, in 'e.g.' for example, this will be considered the end of a sentence.
text = text.replace('.', '.@@')
raw_lines = text.split('@@')
lines = []
for line in raw_lines:
    new_line = line.strip()
    if len(new_line) > 0:
        lines.append(new_line)

# Creates an Extract object for the original text. This will be used for comparison.
original_text = Extract(0)
for line in lines:
    original_text.add_line(Line(line))
original_text.calculate_totals()
original_text.extract_number = "Original"


# This generates Extract objects for every possible extract. It produces sample lengths as close to the sample_length
# variable defined above as possible.
list_of_extracts = []
for y in range(len(original_text.lines)):
    new_extract = Extract(y + 1)
    counter = 0
    last_count = 0
    for x in range(y, len(original_text.lines)):
        counter += len(original_text.lines[x].word_lengths)
        new_extract.add_line(original_text.lines[x])
        if counter >= sample_length:
            if counter - sample_length > sample_length - last_count:
                new_extract.del_last_line()
            break
        last_count = counter

    new_extract.calculate_totals()
    # When nearing the end of the text, if the sample length cannot be made, the loop is ended.
    if counter < sample_length:
        break
    list_of_extracts.append(new_extract)


# Sorts the extracts according to the combined z-score.
def sort_by_z_score(e):
    return e.combined_z_score


list_of_extracts.sort(reverse=False, key=sort_by_z_score)

# Assigns rank numbers based on the sorted list.
rank_number = 1
for extract in list_of_extracts:
    extract.rank_number = rank_number
    rank_number += 1


# The name of the csv file
output_filename = f"{input_filename[:-4]}_output_data.csv"

# Writing to the csv file
with open(output_filename, 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)

    # Headings
    csvwriter.writerow(["Rank", "Sample #", "Words", "AWL", "AWL-Z²", "ASL", "AWL-Z²", "Combined Z"])

    # Values from the original text
    csvwriter.writerow(original_text.get_all_values())

    # Values from the extracts
    for extract in list_of_extracts:
        csvwriter.writerow(extract.get_all_values())

# Creating the folder for the sample texts
path = os.getcwd()
path = f"{path}\\{input_filename[:-4]}_samples"
try:
    os.mkdir(path)
except OSError:
    pass
else:
    print(f"Created directory {path}.")

# Writing the samples to the new folder
for extract in list_of_extracts:
    winner_note = ""
    sample_number = str(extract.extract_number).rjust(3, '0')
    if extract.rank_number == 1:
        winner_note = "_WINNER"
    theFile = open(f"{path}\\sample{sample_number}{winner_note}.txt", "w", encoding='utf-8-sig')
    for line in extract.lines:
        theFile.write(line.string + " ")
    theFile.close()
