from abc import ABC, abstractmethod
from dataclasses import dataclass
import typing as T
from collections.abc import (
	Iterable,
	MappingView,
	MutableMapping,
	MutableSequence,
	Sequence,
	)
import string


class Table(MutableMapping):

	class TableSubset(ABC, MutableSequence):

		def __init__(self, table, table_idx):
			self.table = table
			self.idx = table_idx

		def __iter__(self):
			for idx in range(len(self)):
				yield self[idx]

		def metadata(self, **values):
			return self.table._metadata.setdefault((type(self).__name__, self.idx), {}).update(dict(values))

		@abstractmethod
		def __getitem__(self, idx):
			pass

		@abstractmethod
		def __setitem__(self, idx, item):
			pass

		@abstractmethod
		def __len__(self):
			pass

	class Column(TableSubset):

		def __init__(self, table, idx):
			super().__init__(table, idx)
			if self.idx > getattr(self.table, "_last_column", -1):
				self.table._last_column = self.idx

		def __getitem__(self, idx):
			return self.table._data[(self.idx, idx)]

		def __setitem__(self, idx, item):
			self.table._data[(self.idx, idx)] = item

		def __len__(self):
			return getattr(self.table, "_last_row", -1) + 1

	class Row(TableSubset):

		def __init__(self, table, idx):
			super().__init__(table, idx)
			if self.idx > getattr(self.table, "_last_row", -1):
				self.table._last_row = self.idx

		def __getitem__(self, idx):
			return self.table._data[(idx, self.idx)]

		def __setitem__(self, idx, item):
			self.table._data[(idx, self.idx)] = item

		def __len__(self):
			return getattr(self.table, "_last_column", -1) + 1

	class TableView(ABC, MappingView):

		def __init__(self, table):
			self.table = table
			self.cache = {}

		def __iter__(self):
			for idx in range(len(self)):
				yield self[idx]

		def __getitem__(self, idx: int) -> T.Any:
			if idx < len(self):
				if idx not in self.cache:
					self.cache[idx] = self.subset_factory(idx)
				return self.cache[idx]
			else:
				raise IndexError(idx)

		@abstractmethod
		def subset_factory(self, idx):
			pass

		@abstractmethod
		def __len__(self):
			pass

	class ColumsView(TableView):

		def subset_factory(self, idx):
			return Table.Column(self.table, idx)

		def __len__(self) -> int:
			return getattr(self.table, "_last_column", -1) + 1

	class RowsView(TableView):

		def subset_factory(self, idx):
			return Table.Row(self.table, idx)

		def __len__(self) -> int:
			return getattr(self.table, "_last_row", -1) + 1

	@staticmethod
	def index_alpha_to_num(value: str) -> int:
		if isinstance(value, str):
			if len(value) == 1:
				return ord(val.casefold() - ord("a"))
			elif len(value) > 1:
				return sum(Table.index_num_to_alpha(char) for char in value)
			else:
				raise ValueError(value)
		else:
			raise TypeError(type(value).__name__)

	@staticmethod
	def index_num_to_alpha(value: int) -> str:
		if isinstance(value, int):
			sequence = []
			while value >= 26:
				value, remainder = divmod(value, 26)
				value -= 1
				sequence.insert(0, remainder)
			sequence.insert(0, value)
			return "".join(sequence)

	def __init__(self, data = None, metadata = None):
		self._data = {}
		self._metadata = {}
		self._last_column = -1
		self._last_row = -1
		self._views = {}

	def __getitem__(self, key: T.Tuple[int]) -> T.Any:
		if isinstance(key, tuple) and len(key) == 2:
			try:
				return self._data[key]
			except KeyError:
				raise KeyError(key) from None

	def __setitem__(self, key: T.Tuple[int], value: T.Any):
		if isinstance(key, tuple) and len(key) == 2:
			self._data[key] = value
		else:
			raise TypeError(type(key).__name__)

	@classmethod
	def columnsview(cls, table):
		return cls.RowsView(table)

	@classmethod
	def rowsview(cls, table):
		return cls.ColumnsView(table)

	def columns(self):
		if "columns" not in self._views:
			self._views["columns"] = type(self).columnsview(self)
		return self._views["columns"]

	def rows(self):
		if "rows" not in self._views:
			self._views["rows"] = type(self).rowsview(self)
		return self._views["rows"]

	def get(self, *args, default=None):
		_sentinel = object()
		key = _sentinel

		if len(args) == 1 and not isinstance(args[0], str):
			if isinstance(args[0], Iterable):
				if not isinstance(args[0], Sequence):
					key = tuple(v for v in args[0])
				else:
					key = tuple(args[0])
		elif len(args) == 2 and all(isinstance(a, (int, str)) for a in args):
			key = tuple(args)

		if key is _sentinel:
			raise TypeError("Provide either two arguments or a single sequence of length 2 as key.")

		try:
			return self[key]
		except KeyError:
			if default is not None:
				return default
			raise

	def find(self, value, return_type = int):
		for coords, cell_value in self._data.items():
			if value == cell_value:
				return coords(return_type)
		return None