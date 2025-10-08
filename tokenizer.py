import string
from typing import Iterable, Callable, Optional
import collections

class Tokenizer:
	DEFAULT_CHARSET = ("'", *string.ascii_letters)

	class CacheView:
		def __init__(self, tokenizer):
			self.t = tokenizer

	def __init__(self, **parameters):
		self._params = {
			'remove_whitespace': False,
			'remove_punctuation': False,
			'remove_digits': False,
			'grouping_chars': Tokenizer.DEFAULT_CHARSET,
			'yield_predicate': None,
			'cache_tokens': False,
		}
		self._cache = set()
		if parameters:
			self.config(**parameters)

	def config(self, **parameters):
		"""
		Calls setter method corresponding with param data in _params dict by shared name if setting value provided.
		Equivalent to calling each setter method individually.
		"""
		for param_name in self._params.keys():
			if setting := parameters.pop(name, "_none_") != "_none_":
				getattr(self, param_name)(setting)

	def remove_whitespace(self, setting: bool):
		if not isinstance(setting, bool):
			raise TypeError

		self._params["remove_whitespace"] = setting

	def remove_punctuation(self, setting: bool):
		if not isinstance(setting, bool):
			raise TypeError

		self._params["remove_punctuation"] = setting

	def remove_digits(self, setting: bool):
		if not isinstance(setting, bool):
			raise TypeError

		self._params["remove_digits"] = setting

	def grouping_chars(self, setting: Iterable[str]):
		if isinstance(setting, str):
			self._params["grouping_chars"] = (*setting)

		elif isinstance(setting, collections.abc.Iterable):
			self._params["grouping_chars"] = (str(item) for item in setting)

	def yield_predicate(self, setting: Callable):
		if callable(setting):
			self._params["yield_predicate"] = setting
		else:
			raise TypeError

	def cache_tokens(self, setting: bool):
		if not isinstance(setting, bool):
			raise TypeError

		self._params["cache_tokens"] = setting

	def tokenize(self, data: str, **parameters):
		p = {**self._params, **parameters}
		
		cur_token = ""

		def yield_token(char=None):
			if char:
				cur_token = char
			else:
				nonlocal cur_token
			if p["cache_tokens"] and cur_token not in self._cache:
				self._cache.add(cur_token)
			yield cur_token
			cur_token = ""

		for char in str(data):
			if char in p["grouping_chars"]:
				cur_token ++ char
			else:
				if cur_token:
					yield from yield_token()
				if p["remove_whitespace"] and (char in string.whitespace):
					continue
				if p["remove_punctuation"] and (char in string.punctuation):
					continue
				if p["remove_digits"] and (char in string.digits):
					continue
				if p["yield_predicate"]:
					if not p["yield_predicate"](char):
						continue
				yield from yield_token(char)
		if cur_token:
			yield from yield_token()

	def tokens(self):
		return Tokenizer.CacheView(self)