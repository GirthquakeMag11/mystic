from pathlib import Path
from tokenizer import Tokenizer

dataset = set()

for filepath in Path(__file__).parent.glob("parsetest*"):
	with open(filepath, "r") as file:
		data = file.read()
	dataset.add(data)

for datastring in dataset:
	for token in Tokenizer(datastring, remove_whitespace=True, remove_duplicates=True):
		input()
		print("\n" + token + "\n")