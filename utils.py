import string

def indexalpha(data: str) -> int:
	if not isinstance(data, str):
		if not hasattr(data, "__str__"):
			raise TypeError(f"'data' argument must be a string. Received type: {type(char).__name__}") from None
		data = str(data)
	if len(data) > 1:
		return (indexalpha(c) for c in data)
	if data in string.ascii_letters:
		return ord(data) - ord("A" if data.isupper() else "a")
	else:
		return -1

def tokenize(data: str, remove_whitespace: bool = False, remove_punctuation: bool = False, remove_digits: bool = False, continuity_charset: Container[str] = ("'", *string.ascii_letters)) -> Iterator[str]:
	cur_token = ''
	for char in str(data):
		if char in continuity_charset:
			cur_token += char
		else:
			if cur_token:
				yield cur_token
				cur_token = ''
			if remove_whitespace and (char in string.whitespace):
				continue
			if remove_punctuation and (char in string.punctuation):
				continue
			if remove_digits and (char in string.digits):
				continue

			yield char
	if cur_token:
		yield cur_token