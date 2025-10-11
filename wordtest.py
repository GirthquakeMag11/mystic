from pathlib import Path
from tokenizer import Tokenizer


with open(Path(__file__).parent / "en_US.dic", "r") as file:
	data = file.read()

test_tokenizer = Tokenizer()
# Default params test

print("Press Enter for next token")
next_token = test_tokenizer

for token in test_tokenizer.tokenize(data, remove_whitespace=True, deduplicate_output=True):
	input()
	print(token)

