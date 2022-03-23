import random
import string

# Generate a random sequence of letters and numbers of a given length
def generate_random_string(length=8):
    letters_and_digits = string.ascii_letters + string.digits
    random_string = ''.join(random.sample(letters_and_digits, length))
    return random_string