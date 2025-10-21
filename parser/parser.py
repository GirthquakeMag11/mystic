import string
import token

class Parser:

	def __init__(self, data: str = "", **parameters):
		self._data = data
		self._parameters = dict(parameters)
		self._cur_token = ""
		self._queued_tokens = []
		self._idx = -1
		self._seen = set()

	@property
	def _cur_char(self):
		if self._data.strip() and (self._idx > -1):
			return self._data[self._idx]

	def _next_chars(self, stop_char: str = None, stop_idx: int = None):
		if stop_idx:
			return self._data[self._idx:self._idx + int(stop_idx)]
		elif char:
			i = 0
			while self._data[self._idx + i] == char:
				i += 1
			return self._next_chars(stop_idx=i+1)

	def _to_char(self, to_char: str = None, to_idx: int = None):
		if to_idx:
			if len(self._data) > to_idx + 1:
				return self._data[self._idx:to_idx + 1]
			elif len(self._data) <= to_idx + 1:
				return self._data[self._idx:]
		elif to_char:
			if (char_idx := self._data.find(to_char, self._idx + 1)) > 0:
				return self._to_char(to_idx=char_idx)
			else:
				return ""

	def _queue(self, *tokens):
		self._queue_current()
		self._queue_current.extend([t for t in tokens if self._queue_check(t)])

	def _queue_current(self):
		if self._queue_check(self._cur_token):
			self._queued_tokens.append(self._cur_token)
			self._cur_token = ""

	def _queue_check(self, token):
		if self._parameters.get("omit_whitespace", False) and (not token.strip()):
			return False
		if self._parameters.get("deduplicate", False):
			if token in self._seen:
				return False
			else:
				self._seen.add(token)
		return token

	def _group_char(self):
		if self._cur_char in token.Text.GROUPING_CHARS.value:
			self._cur_token += self._cur_char
			return True
		return False

	def _compound_char(self):
		return self._cur_char in token.Text.COMPOUND_CHARS.value

	def _special_compounds(self):
		if self._parameters.get("ellipsis", True):
			if self._cur_char == "." and self._next_chars(stop_idx=3) == token.Text.ELLIPSIS.value:
				self._queue(token.Text.ELLIPSIS.value)
				self._idx += 2
				return True

		if self._cur_char == ":":

			if self._parameters.get("emojis", True):
				to_next_colon = self._to_char(stop_char=":")
				if to_next_colon.strip() and not any(char in string.whitespace for char in to_next_colon):
					self._queue(to_next_colon)
					self._idx += (len(to_next_colon) + 1)
					return True

			if self._parameters.get("urls", True):
				if any(self._cur_token.strip().casefold().startswith(const) for const in token.URL.PREFIX.value):
					self._cur_token += self._cur_char
					return True