# Use the set of English words containing lower-case letters with no punctuation
import random
import re

possible_words = []

def generate_word_set(num_words, file_path):
    dic = {}
    for _ in range(num_words):
        found_unique_word = False
        random_word = ""
        while not found_unique_word:
            # only grab letters
            random_word = re.sub(r"[\W_]+", "", random.sample(possible_words, 1)[0])
            if random_word not in dic:
                found_unique_word = True

        dic[random_word] = random.randint(2, 25)

    # Save the dictionary to a txt file for the test to read
    f = open(file_path, "w")
    f.write(str(dic))
    f.close()


otp = open("tests/word_sets/hp_otp.txt", "r")
possible_words = set(otp.read().lower().split())

# Generate new word sets
#  NOTE: Committing these will fail the test_create_wordcloud test
generate_word_set(20, "tests/word_sets/small_word_set.txt")
print("Generaed small word set...")

generate_word_set(100, "tests/word_sets/medium_word_set.txt")
print("Generaed medium word set...")

generate_word_set(500, "tests/word_sets/large_word_set.txt")
print("Generaed large word set...")

generate_word_set(1000, "tests/word_sets/huge_word_set.txt")
print("Generaed huge word set...")
