from abc import ABC, abstractmethod
import typing as T
from collections.abc import (
	Iterable,
	MappingView,
	MutableMapping,
	MutableSequence,
	Sequence,
	)
from string import ascii_uppercase

class Table(MutableMapping):

	class TableSubset(ABC, MutableSequence):

		def __init_subclass__(cls, *args, **kwargs):
			super().__init_subclass__(cls)
			abstract_methods = ("__getitem__","__setitem__","__len__")
			for mandatory in abstract_methods:
				if not callable(getattr(cls, mandatory, None)):
					raise TypeError(f"TableSubset subclass {cls.__name__} missing required method {mandatory}")

		def __init__(self, table: "Table", table_idx: int):
			self.table = table
			self.idx = table_idx

		def __iter__(self) -> T.Iterable[T.Any]:
			for idx in range(len(self)):
				yield self[idx]

		def metadata(self, **values) -> T.Dict:
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

		def __init__(self, table: "Table", idx: int):
			super().__init__(table, idx)
			if self.idx > getattr(self.table, "_last_column", -1):
				self.table._last_column = self.idx

		def __getitem__(self, idx: int) -> T.Any:
			return self.table[(self.idx, idx)]

		def __setitem__(self, idx: int, item: T.Any):
			self.table[(self.idx, idx)] = item

		def __len__(self) -> int:
			return getattr(self.table, "_last_row", -1) + 1

	class Row(TableSubset):

		def __init__(self, table: "Table", idx: int):
			super().__init__(table, idx)
			if self.idx > getattr(self.table, "_last_row", -1):
				self.table._last_row = self.idx

		def __getitem__(self, idx: int) -> T.Any:
			return self.table[(idx, self.idx)]

		def __setitem__(self, idx: int, item: T.Any):
			self.table[(idx, self.idx)] = item

		def __len__(self) -> int:
			return getattr(self.table, "_last_column", -1) + 1

	class TableView(ABC, MappingView):

		def __init_subclass__(cls, *args, **kwargs):
			super().__init_subclass__(cls)
			abstract_methods = ("subset_factory", "__len__")
			for mandatory in abstract_methods:
				if not callable(getattr(cls, mandatory, None)):
					raise TypeError(f"TableView subclass {cls.__name__} missing required method {mandatory}")

		def __init__(self, table: "Table"):
			self.table = table
			self.cache = {}

		def __iter__(self) -> T.Iterable["Table.TableSubset"]:
			for idx in range(len(self)):
				yield self[idx]

		def __getitem__(self, idx: int) -> "Table.TableSubset":
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

	class ColumnsView(TableView):

		def subset_factory(self, idx: int) -> "Table.TableSubset":
			return Table.Column(self.table, idx)

		def __len__(self) -> int:
			return getattr(self.table, "_last_column", -1) + 1

	class RowsView(TableView):

		def subset_factory(self, idx: int) -> "Table.TableSubset":
			return Table.Row(self.table, idx)

		def __len__(self) -> int:
			return getattr(self.table, "_last_row", -1) + 1

	@staticmethod
	def index_alpha_to_num(value: str) -> int:
		if isinstance(value, str):
			value = value.strip().upper()
			result = 0
			for char in value:
				if char not in ascii_uppercase:
					raise ValueError(f"Invalid character {char} in index {value}")
				result = result * 26 + ascii_uppercase.index(char)
			return result

	@staticmethod
	def index_num_to_alpha(value: int) -> str:
		if isinstance(value, int):
			if value < 0:
				raise ValueError(f"Invalid index integer {value}")
			sequence = []
			while value >= 26:
				value, remainder = divmod(value, 26)
				value -= 1
				sequence.insert(0, ascii_uppercase[remainder])
			sequence.insert(0, ascii_uppercase[value])
			return "".join(sequence)

	def __init__(self, data = None, metadata = None):
		self._data = {}
		self._metadata = {}
		self._last_column = -1
		self._last_row = -1
		self._views = {}

	def shift_last_index(self, index_type, val):
		l_idx = f"_last_{str(index_type).strip().casefold()}"
		if int(val) > getattr(self, l_idx, -1):
			setattr(self, l_idx, int(val))

	def __getitem__(self, key: T.Tuple[int]) -> T.Any:
		if isinstance(key, tuple) and len(key) == 2 and all(isinstance(k, int) for k in key):
			try:
				return self._data[key]
			except KeyError:
				raise KeyError(key) from None

	def __setitem__(self, key: T.Tuple[int], value: T.Any):
		if isinstance(key, tuple) and len(key) == 2 and all(isinstance(k, int) for k in key):
			self._data[key] = value
			self.shift_last_index("column", key[0])
			self.shift_last_index("row", key[1])
		else:
			raise TypeError(type(key).__name__)

	@classmethod
	def columnsview(cls, table: "Table") -> "Table.ColumnsView":
		return cls.ColumnsView(table)

	@classmethod
	def rowsview(cls, table: "Table") -> "Table.RowsView":
		return cls.RowsView(table)

	def columns(self) -> "Table.TableView":
		if "columns" not in self._views:
			self._views["columns"] = type(self).columnsview(self)
		return self._views["columns"]

	def rows(self) -> "Table.TableView":
		if "rows" not in self._views:
			self._views["rows"] = type(self).rowsview(self)
		return self._views["rows"]
