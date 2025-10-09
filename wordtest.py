from pathlib import Path

with open(Path(__file__).parent / "en_US.dic", "r") as file:
	data = file.readlines()

names = []
words = []
other = []

for entry in data:
	word = entry.strip("\n").split("/")[0]
	if word[0].islower():
		words.append(word)
	else:
		other.append(word)

with open(Path.cwd() / "words.txt", "w") as wordfile:
	wordfile.write("\n".join(words))