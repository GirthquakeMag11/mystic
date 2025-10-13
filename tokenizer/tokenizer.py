import string


class Tokenizer:
	GROUPING_CHARS = ("'","’", *string.ascii_letters, *string.digits)
	COMPOUND_CHARS = (".","-","–","—","@",",","/","_",":")
	ELLIPSIS = "..."

	@classmethod
	def fromfile(cls, filepath):
		def generate_char_from_file():
			with open(filepath, "r") as f:
				idx = yield
				while True:
					f.seek(idx)
					char = f.read(1)
					index = yield char
		return cls(generator=generate_char_from_file())

	def __init__(self, data: str = "", generator: Generator = None):
		self.data = data
		self.cur_token = ""
		self.queued_tokens = []
		self.idx = -1
		if generator:
			self.generator = generator

	@property
	def _cur_char(self):
		if hasattr(self, "generator"):
			try:
				return self.generator.send(self.idx)
			except TypeError as e:
				if "just-started generator" in str(e):
					next(self.generator)
					return self._cur_char
				else:
					raise
		if self.data and (self.idx > -1):
			return self.data[self.idx]

	def _queue(self, *token):
		self.queued_tokens.extend([t.strip() for t in token if t.strip()])
		if self.cur_token in token:
			self.cur_token = ""

	def _group_char(self):
		if self._cur_char in Tokenizer.GROUPING_CHARS:
			self.cur_token += self._cur_char
			return True
		return False

	def _compound_char(self):
		if self.data[self.idx] in Tokenizer.GROUPING_CHARS:
			return True
		return False

	def _special_compounds(self):
		if self._cur_char == ".":
			# Ellipsis check
			if self.data[self.idx:self.idx+3] == Tokenizer.ELLIPSIS:
				self._queue(self.cur_token, Tokenizer.ELLIPSIS)
				self.idx += 2
				return True
		elif self._cur_char == ":":
			# Emoji check
			if (next_colon := data.find(":", self.idx + 1)) > 0:
				next_colon += 1
				possible_emoji = self.data[self.idx:next_colon]
				if not any(char in string.whitespace for char in possible_emoji):
					self._queue(self.cur_token, possible_emoji)
					self.idx = next_colon
					return True
			# URL prefix check
			if self.cur_token.strip().casefold().startswith("http"):
				self.cur_token += self._cur_char
				return True
			# fallback (just a colon)
			self._queue(self.cur_token, ":")
			return True
		return False

	def _standard_compound(self):
		"""Normal compound character check for things like compound words, dates, times. Ex: '08-12-2015', 'over-blown', '12:15'."""
		if self.data[self.idx - 1] in Tokenizer.GROUPING_CHARS and self.data[self.idx + 1] in Tokenizer.GROUPING_CHARS:
			self.cur_token += self._cur_char
			return True
		return False

	def _shift_idx(self):
		try:
			n = self.data[self.idx + 1]
			self.idx += 1
			return True
		except IndexError:
			return False

	def __iter__(self):
		return self

	def __next__(self):
		while True:
			if self.queued_tokens:
				return self.queued_tokens.pop(0)

			if self._shift_idx():
				if self._group_char():
					continue
				if self._compound_char():
					if self._special_compounds():
						continue
					if self._standard_compound():
						continue
				self._queue(self.cur_token, self.data[self.idx])
			elif self.cur_token:
				self._queue(self.cur_token)
			else:
				break

		raise StopIteration

if __name__ == "__main__":
	input()
	for token in Tokenizer("hello world my name is hp lovecraft and this is my cat niggerman"):
		input()
		print(token)