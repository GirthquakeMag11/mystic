import string
import enum
from dataclasses import dataclass, field


class YAML(enum.Enum):
	START_END = "---"

	@dataclass
	class Title:
		value: str
		def __str__(self):
			return f"title: {self.value}"

	@dataclass
	class Tag:
		value: str
		def __str__(self):
			return f"  - {self.value}"

	@dataclass
	class Alias:
		value: str
		def __str__(self):
			return f"  - {self.value}"

	@dataclass
	class Property:
		name: str
		value: Any
		def __str__(self):
			return f"{self.name}: {self.value}"

class Parser:
	GROUPING_CHARS = ("'","’", *string.ascii_letters, *string.digits)
	COMPOUND_CHARS = (".","-","–","—","@",",","/","_",":")
	HTTP = "http"
	HTTPS = "https"
	ELLIPSIS = "..."

	def __init__(self, data: str = '', lines: Iterable[str] = None, **parameters):
		self._data = data
		self._lines = [line for line in lines] if lines is not None else [self._data.splitlines()]
		self._ellipsis = parameters.pop("ellipsis", True)
		self._deduplicate = parameters.pop("deduplicate_output", False)
		self._omit_whitespace = parameters.pop("omit_whitespace", False)
		self._emojis = parameters.pop("attempt_emojis", True)
		self._urls = parameters.pop("attempt_urls", True)
		self._yaml = parameters.pop("attempt_yaml", True)
		self._markdown = parameters.pop("attempt_markdown", True)

		self._cur_token = ""
		self._queued_tokens = []
		self._idx = -1
		self._seen = set()

	@property
	def _cur_char(self):
		if self._data.strip() and (self._idx > -1):
			return self._data[self._idx]

	def _next_chars(self, char: str = None, idx: int = None):
		if idx:
			return self._data[self._idx:self._idx + int(idx)]
		elif char:
			i = 0
			while self._data[self._idx + i] == char:
				i += 1
			return self._next_chars(idx=i+1)


	def _to_char(self, char: str = None, idx: int = None):
		"""
		> Slices _data from _idx to defined stop char/idx.
		> Start & end inclusive
		> If _data too short for defined stop idx or does not contain defined stop char:
		> 	Returns _data starting from _idx
		"""
		if idx:
			if len(self._data) > idx + 1:
				return self._data[self._idx:idx + 1]
			elif len(self._data) <= idx + 1:
				return self._data[self._idx:]
		elif char:
			if (char_idx := self._data.find(char, self._idx + 1)) > 0:
				return self._to_char(idx=char_idx)
			else:
				return ""


	def _queue(self, *tokens):
		self._queue_current()
		self._queued_tokens.extend([t for t in tokens if self._queue_check(t)])

	def _queue_current(self):
		if self._queue_check(self._cur_token):
			self._queued_tokens.extend(self._cur_token)
			self._cur_token = ""

	def _queue_check(self, token):
		if self._omit_whitespace and (not token.strip()):
			return False
		if self._deduplicate:
			if token in self._seen:
				return False
			else:
				self._seen.add(token)
		return token

	def _group_char(self):
		if self._cur_char in Parser.GROUPING_CHARS:
			self._cur_token += self._cur_char
			return True
		return False

	def _compound_char(self):
		return bool(self._cur_char in Parser.COMPOUND_CHARS)

	def _special_compounds(self):
		# Ellipsis check
		if self._ellipsis:
			if self._cur_char == "." and self._next_chars(idx=3) == Parser.ELLIPSIS:
				self._queue(Parser.ELLIPSIS)
				self._idx += 2
				return True

		# Emoji check
		if self._emojis and self._cur_char == ":":
			to_next_colon = self._to_char(char=":")
			if to_next_colon.strip() and not any(char in string.whitespace for char in to_next_colon):
				self._queue(to_next_colon)
				self._idx += (len(to_next_colon) + 1)
				return True

		# URL prefix check
		if self._urls and self._cur_char == ":":
			if any(self._cur_token.strip().casefold().startswith(const) for const in (Parser.HTTP, Parser.HTTPS)):
				self._cur_token += self._cur_char
				return True

		# YAML check
		"""not written yet"""

		# Markdown check
		if self._markdown:
			# Markdown header check
			if self._cur_char == "#":
				hashtag_sequence = self._next_chars("#")
				if self._data[self._idx - 1] == "\n":
					try:
						if not self._data[self._idx + len(hashtag_sequence)] in string.whitespace:
							self._queue(hashtag_sequence)
							self._idx += len(hashtag_sequence)
							return True
					except IndexError:
						pass
			# Markdown bullet check
			if self._cur_char == "-":
				if self._next_chars(len(Markdown.BULLET) - 1) == Markdown.BULLET:
					# Markdown checkbox check
					possible_checkbox = self._next_chars(len(Markdown.CHECKBOX_FALSE) - 1)
					if possible_checkbox == Markdown.CHECKBOX_FALSE:
						self._queue(Markdown.CHECKBOX_FALSE)
						self._idx += len(Markdown.CHECKBOX_FALSE)
						return True
					elif possible_checkbox == Markdown.CHECKBOX_TRUE:
						self._queue(Markdown.CHECKBOX_TRUE)
						self._idx += len(Markdown.CHECKBOX_TRUE)
						return True
					else:
						self._queue(Markdown.BULLET)
						self._idx += len(Markdown.BULLET)
						return True

		# No special compound identified
		return False

	def _standard_compound(self):
		try:
			before = bool(self._data[self._idx - 1] in Parser.GROUPING_CHARS)
		except IndexError:
			before = True
		try:
			after = bool(self._data[self._idx + 1] in Parser.GROUPING_CHARS)
		except IndexError:
			after = False
		return bool(before and after)

	def _shift_idx(self):
		if len(self._data) - 1 >= self._idx + 1:
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

				self._queue(self._cur_char)

			elif self._cur_token:
				self._queue_current()

			else:
				break

		raise StopIteration