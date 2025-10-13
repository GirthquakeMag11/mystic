import string

class Tokenizer:
	GROUPING_CHARS = ("'","’", *string.ascii_letters, *string.digits)
	COMPOUND_CHARS = (".","-","–","—","@",",","/","_",":")

	def __init__(self, data: str, remove_whitespace: bool = False, remove_duplicates: bool = False):
		if isinstance(data, str):
			self._data = data
		else:
			raise TypeError(f"Tokenizer data must be a string, provided type: '{type(data).__name__}'")
		self._rw = remove_whitespace
		self._rd = remove_duplicates
		self._ct = {}

	def __iter__(self) -> Iterator[str]:
		cur_token = ""
		seen = set()
		data = self._data

		def check_remove_dup(token):
			if self._rd:
				if token in seen:
					return False
				else:
					seen.add(token)
			return True

		def check_remove_ws(token):
			if self._rw:
				token = "".join([c for c in token if c not in string.whitespace])
				if token.strip():
					return token.strip()
				return False
			return token

		def yield_token(token=None):
			nonlocal cur_token
			token_to_yield = token if token is not None else cur_token
			if token_to_yield:
				if check_remove_dup(token_to_yield):
					if valid_token := check_remove_ws(token_to_yield):
						yield valid_token
				self._ct.setdefault(token_to_yield, self._ct.get(token_to_yield, 0) + 1)
				cur_token = ""

		def flush_yield(token):
			if cur_token:
				yield from yield_token()
			yield from yield_token(token)

		i = -1
		while True:
			try:
				i += 1
				char = data[i]
				if char in Tokenizer.GROUPING_CHARS:
					cur_token += char
					continue

				if char in Tokenizer.COMPOUND_CHARS:
					if char == ".":
						if data[i:i+3] == "...":
							yield from flush_yield("...")
							i = i + 2
							continue

					if char == ":":
						if (next_colon := data.find(":", i + 1)) > 0:
							possible_emoji = data[i:next_colon + 1]
							if not any(c in string.whitespace for c in possible_emoji):
								yield from flush_yield(possible_emoji)
								i = next_colon + 1
								continue
						if cur_token.strip().casefold() == "https":
							cur_token += char
							continue

						yield from flush_yield(":")
						continue

					if data[i - 1] in Tokenizer.GROUPING_CHARS and data[i + 1] in Tokenizer.GROUPING_CHARS:
						cur_token += char
						continue

				yield from flush_yield(char)

			except IndexError as e:
				if "index out of range" in str(e):
					pass

		if cur_token:
			yield from yield_token()