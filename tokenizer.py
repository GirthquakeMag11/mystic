from typing import Iterable, Callable, Optional, Iterator, Set, Any
import collections.abc
import warnings
import string
import hashlib

class Tokenizer:
	"""
	Flexible, reusable tokenizer for breaking strings into tokens based on configurable grouping,
	character exclusion, and predicate functions.

	Features:
	- Configurable grouping characters (e.g., what counts as a valid multi-character or 'word' token)
	- Optional removal of whitespace, punctuation, or digits
	- Custom predicate for filtering yielded tokens
	- Caching of seen tokens for batch or post-processing
	"""
	DEFAULT_CHARSET = ("'", *string.ascii_letters, *string.digits)

	class CacheView:
		def __init__(self, tokenizer: "Tokenizer"):
			self.t = tokenizer

		def __iter__(self) -> Iterator[str]:
			yield from self.t._cache

		def __contains__(self, item: str) -> bool:
			return bool(item in self.t._cache)

		def __len__(self) -> int:
			return len(self.t._cache)

		def __hash__(self) -> int:
			hasher = hashlib.md5()
			for s in self.t._cache:
				hasher.update(s.encode())
			return int.from_bytes(hasher.digest())

		def add(self, item) -> "Tokenizer.CacheView":
			self.t._cache.add(item)
			return self

		def remove(self, item) -> "Tokenizer.CacheView":
			self.t._cache.discard(item)
			return self

	def __init__(self, initial_data=None, **parameters) -> None:
		self._params = {
			'remove_whitespace': False,
			'remove_punctuation': False,
			'remove_digits': False,
			'grouping_chars': Tokenizer.DEFAULT_CHARSET,
			'yield_predicate': None,
			'cache_tokens': False,
			'post_processor': None,
			'deduplicate_output': True,
		}
		self._data = set()
		self._cache = set()
		self._context = None
		if parameters:
			self.config(**parameters)

	def config(self, **parameters: Any) -> "Tokenizer":
		"""
		Calls setter method corresponding with param data in _params dict by shared name if setting value provided.
		Equivalent to calling each setter method individually.
		Ignores unknown parameters, but warns the user when encountered.
			NOTE: This means typos in arguments will not raise exceptions.
		"""
		for param_name, value in parameters.items():
			if param_name in self._params:
				getattr(self, param_name)(value)
			else:
				warnings.warn(
					f"Ignoring unknown parameter '{param_name}' in Tokenizer.config()",
					UserWarning, stacklevel=2
					)
		return self

	def remove_whitespace(self, setting: bool) -> "Tokenizer":
		if not isinstance(setting, bool):
			raise TypeError("'remove_whitespace' must be a boolean value")
		self._params["remove_whitespace"] = setting
		return self

	def remove_punctuation(self, setting: bool) -> "Tokenizer":
		if not isinstance(setting, bool):
			raise TypeError("'remove_punctuation' must be a boolean value")
		self._params["remove_punctuation"] = setting
		return self

	def remove_digits(self, setting: bool) -> "Tokenizer":
		if not isinstance(setting, bool):
			raise TypeError("'remove_digits' must be a boolean value")
		self._params["remove_digits"] = setting
		return self

	def grouping_chars(self, setting: Iterable[str]) -> "Tokenizer":
		if isinstance(setting, str):
			self._params["grouping_chars"] = tuple(setting)

		elif isinstance(setting, collections.abc.Iterable):
			try:
				self._params["grouping_chars"] = tuple(str(item) for item in setting)
			except Exception as e:
				raise TypeError("'grouping_chars' must be an iterable of characters or objects with a properly implemented __str__ method.") from e
		else:
			raise TypeError("'grouping_chars' must be an iterable of characters or objects with a properly implemented __str__ method.")
		return self

	def yield_predicate(self, setting: Callable) -> "Tokenizer":
		if setting is not None and not callable(setting):
			raise TypeError("'yield_predicate' must be callable or None.")
		self._params["yield_predicate"] = setting
		return self

	def cache_tokens(self, setting: bool) -> "Tokenizer":
		if not isinstance(setting, bool):
			raise TypeError("'cache_tokens' must be a boolean value.")
		self._params["cache_tokens"] = setting
		return self

	def post_processor(self, setting: Callable) -> "Tokenizer":
		if setting is not None and not callable(setting):
			raise TypeError("'post_processor' must be callable or None.")
		self._params["post_processor"] = setting
		return self

	# # #

	def tokens(self) -> "Tokenizer.CacheView":
		"""
		Get a view of the current token cache.
		"""
		return Tokenizer.CacheView(self)

	# # #

	def __enter__(self, data: str = None, **parameters):
		if data:
			self._data.add(str(data))
		self._context = functools.partial(self.tokenize, None, **parameters)
		return self

	def __exit__(self, exc_type, exc_val, traceback):
		self._context = None

	# # #

	def tokenize(self, data: str = None, **parameters) -> Iterator[str]:
		"""
		Splits input strings into tokens according to current configuration.
		Any parameters provided here will be used instead of the current Tokenizer's settings
		without overwriting them.
		"""
		p = {**self._params, **parameters}

		if getattr(self, "_context", None) is not None:
			if data is not None:
				self._data.add(str(data))
			yield from self._context()
		
		cur_token = ""
		seen = set()

		def yield_token(token=None):
			nonlocal cur_token
			token_to_yield = token if token is not None else cur_token
			if not token_to_yield:
				return
			if p["deduplicate_output"]:
				nonlocal seen
				if token_to_yield in seen:
					if token_to_yield == cur_token:
						cur_token = ""
					return
				else:
					seen.add(token_to_yield)
			if p["post_processor"]:
				token_to_yield = p["post_processor"](token_to_yield)
			if p["cache_tokens"]:
				self._cache.add(token_to_yield)
			yield token_to_yield
			cur_token = ""

		if not data:
			return

		i = -1
		data = str(data)
		for char in data:
			i += 1
			if char in p["grouping_chars"]:
				cur_token += char
			if char == ".":
				try:
					if extension := ext_match(data[i]):
						cur_token += extension
						i += len(extension)

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