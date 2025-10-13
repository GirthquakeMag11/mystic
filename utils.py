import string

def indexalpha(data: str) -> int:
	if not isinstance(data, str):
		if not hasattr(data, "__str__"):
			raise TypeError(f"'data' argument must be a string. Received type: {type(char).__name__}")
		data = str(data)
	if len(data) > 1:
		return (indexalpha(c) for c in data)
	if data in string.ascii_letters:
		return ord(data) - ord("A" if data.isupper() else "a")
	else:
		return -1
