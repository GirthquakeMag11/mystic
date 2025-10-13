import string
from typing import Generator

class Tokenizer:
	GROUPING_CHARS = ("'","’", *string.ascii_letters, *string.digits)
	COMPOUND_CHARS = (".","-","–","—","@",",","/","_",":")
	ELLIPSIS = "..."

	@classmethod
	def fromfile(cls, filepath, encoding="utf-8"):
		def generate_char_from_file():
			with open(filepath, "r", encoding=encoding) as f:
				idx = yield
				while True:
					f.seek(idx)
					char = f.read(1)
					idx = yield char
		generator = generate_char_from_file()
		next(generator)
		return cls(generator=generator)

	def __init__(self, data: str = "", generator: Generator = None, **parameters):
		self._data = data
		self._generator = generator
		self._cur_token = ""
		self._queued_tokens = []
		self._idx = -1
		self._seen = set()
		self._deduplicate_output = parameters.pop("deduplicate_output", False)

	@property
	def _cur_char(self):
		if self._generator:
			try:
				return self._generator.send(self._idx)
			except TypeError as e:
				if "just-started generator" in str(e):
					next(self._generator)
					return self._generator.send(self._idx)
				else:
					raise
		if self._data and (self._idx > -1):
			return self._data[self._idx]

	def _queue(self, *token):
		self._queued_tokens.extend([t.strip() for t in token if (t.strip() and self._duplicate_check(t))])
		if self._cur_token in token:
			self._cur_token = ""

	def _group_char(self):
		if self._cur_char in Tokenizer.GROUPING_CHARS:
			self._cur_token += self._cur_char
			return True
		return False

	def _compound_char(self):
		return bool(self._cur_char in Tokenizer.GROUPING_CHARS)

	def _special_compounds(self):
		if self._cur_char == ".":
			# Ellipsis check
			if self._data[self._idx:self._idx+3] == Tokenizer.ELLIPSIS:
				self._queue(self._cur_token, Tokenizer.ELLIPSIS)
				self._idx += 2
				return True
		elif self._cur_char == ":":
			# Emoji check
			if (next_colon := data.find(":", self._idx + 1)) > 0:
				next_colon += 1
				possible_emoji = self._data[self._idx:next_colon]
				if not any(char in string.whitespace for char in possible_emoji):
					self._queue(self._cur_token, possible_emoji)
					self._idx = next_colon
					return True
			# URL prefix check
			if self._cur_token.strip().casefold().startswith("http"):
				self._cur_token += self._cur_char
				return True
			# fallback (just a colon)
			self._queue(self._cur_token, ":")
			return True
		return False

	def _standard_compound(self):
		"""Normal compound character check for things like compound words, dates, times. Ex: '08-12-2015', 'over-blown', '12:15'."""
		if self._data[self._idx - 1] in Tokenizer.GROUPING_CHARS and self._data[self._idx + 1] in Tokenizer.GROUPING_CHARS:
			self._cur_token += self._cur_char
			return True
		return False

	def _shift_idx(self):
		if self._data:
			try:
				n = self._data[self._idx + 1]
				self._idx += 1
				return True
			except IndexError:
				return False
		elif self._generator:
			self._idx += 1
			return True
		return False

	def _duplicate_check(self, token):
		if self._deduplicate_output:
			if token in self._seen:
				return False
			else:
				self._seen.add(token)
		return token

	def __iter__(self):
		return self

	def __next__(self):
		while True:
			if self._queued_tokens:
				return self._queued_tokens.pop(0)

			if self._shift_idx():
				if self._group_char():
					continue
				if self._compound_char():
					if self._special_compounds():
						continue
					if self._standard_compound():
						continue


				self._queue(self._cur_token, self._cur_char)
			elif self._cur_token:
				self._queue(self._cur_token)
			else:
				break

		raise StopIteration
