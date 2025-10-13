from typing import Generator
import fnmatch
import string

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

	def __init__(self, data: str = '', **parameters):
		self._data = data if data.strip() else None
		self._generator = parameters.pop("generator", None)
		self._cur_token = ""
		self._queued_tokens = []
		self._idx = -1
		self._seen = set()
		self._deduplicate_output = parameters.pop("deduplicate_output", False)
		self._emojis = parameters.pop("attempt_emojis", True)
		self._urls = parameters.pop("attempt_urls", True)
		self._ellipsis = parameters.pop("ellipsis", True)
		self._omit_whitespace = parameters.pop("omit_whitespace", True)
		self._match_pattern = parameters.pop("match_pattern", "**")

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
		elif self._data and (self._idx > -1):
			return self._data[self._idx]

	def _queue(self, *token):
		self._queued_tokens.extend([t for t in token if self._queue_check(t)])
		if self._cur_token in token:
			self._cur_token = ""

	def _queue_check(self, token):
		if not fnmatch.fnmatch(token, self._match_pattern):
			return False
		if self._omit_whitespace:
			if not token.strip():
				return False
		if self._deduplicate_output:
			if token in self._seen:
				return False
			else:
				self._seen.add(token)
		return token

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
			if self._ellipsis and self._data[self._idx:self._idx+3] == Tokenizer.ELLIPSIS:
				self._queue(self._cur_token, Tokenizer.ELLIPSIS)
				self._idx += 2
				return True
		elif self._cur_char == ":":
			# Emoji check
			if self._emojis and (next_colon := data.find(":", self._idx + 1)) > 0:
				next_colon += 1
				possible_emoji = self._data[self._idx:next_colon]
				if not any(char in string.whitespace for char in possible_emoji):
					self._queue(self._cur_token, possible_emoji)
					self._idx = next_colon
					return True
			# URL prefix check
			if self._urls and self._cur_token.strip().casefold().startswith("http"):
				self._cur_token += self._cur_char
				return True
			# fallback (just a colon- not part of compound token)
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
