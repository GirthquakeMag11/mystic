from abc import ABC, abstractmethod
from collections.abc import MutableMapping, MappingView, MutableSequence

class TableSubset(ABC, MutableSequence):

	def __init__(self, table, idx):
		self.table = table
		self.idx = idx

	def __iter__(self):
		for idx in range(len(self)):
			yield self[idx]

	@abstractmethod
	def metadata(self, **parameters):
		pass

	@abstractmethod
	def __getitem__(self, idx):
		pass

	@abstractmethod
	def __setitem__(self, idx, item):
		pass

	@abstractmethod
	def __len__(self):
		pass

	@classmethod
	def from_iter(cls, table, idx, data):
		new = cls(table, idx)
		for i, v in enumerate(data):
			new[i] = v
		return new

class Column(TableSubset):

	def __init__(self, table, idx):
		super().__init__(table, idx)
		if self.idx > self.table._last_col:
			self.table._last_col = self.idx

	def __getitem__(self, idx):
		return self.table._data[(self.idx, idx)]

	def __setitem__(self, idx, item):
		self.table._data[(self.idx, idx)] = item

	def __len__(self):
		return getattr(self.table, "_last_row", -1) + 1

	def metadata(self, **parameters):
		return self.table._col_meta.setdefault(self.idx, {}) |= dict(parameters)

class Row(TableSubset):

	def __init__(self, table, idx):
		super().__init__(table, idx)
		if self.idx > self.table._last_row:
			self.table._last_row = self.idx

	def __getitem__(self, idx):
		return self.table._data[(idx, self.idx)]

	def __setitem__(self, idx, item):
		self.table._data[(idx, self.idx)] = item

	def __len__(self):
		return getattr(self.table, "_last_col", -1) + 1

	def metadata(self, **parameters):
		return self.table._row_meta.setdefault(self.idx, {}) |= dict(parameters)

class TableView(ABC, MappingView):

	def __init__(self, table):
		self.table = table

	def __iter__(self):
		for idx in range(len(self)):
			yield self[idx]

	@property
	def cache(self):
		return self.__dict__.setdefault("cache", {})

	@abstractmethod
	def __getitem__(self, idx):
		pass

	@abstractmethod
	def __setitem__(self, idx, value):
		pass

	@abstractmethod
	def __len__(self):
		pass

class ColumnsView(TableView):

	def __getitem__(self, idx: int) -> Any:
		if idx < len(self):
			return self.cache.setdefault(idx, Column(self.table, idx))
		else:
			raise IndexError(idx) from None

	def __setitem__(self, idx: int, value: Iterable) -> None:
		if hasattr(value, "__iter__"):
			self.cache[idx] = Column.from_iter(self.table, idx, data = iter(value))

	def __len__(self) -> int:
		return getattr(self.table, "_last_col", -1) + 1

class RowsView(TableView):

	def __getitem__(self, idx: int) -> Any:
		if idx < len(self):
			return self.cache.setdefault(idx, Row(self.table, idx))
		else:
			raise IndexError(idx) from None

	def __setitem__(self, idx: int, value: Iterable) -> None:
		if hasattr(value, "__iter__"):
			self.cache[idx] = Row.from_iter(self.table, idx, data = iter(value))

	def __len__(self) -> int:
		return getattr(self.table, "_last_row", -1) + 1

class Table(MutableMapping):

	def __init__(self):
		self._data = {}
		self._last_col = -1
		self._last_col = -1
		self._views = {}
		self._col_meta = {}
		self._row_meta = {}

	def __getitem__(self, key: int | str) -> Any:
		if isinstance(key, tuple) and len(key) == 2:
			return self._data[key]
		elif isinstance(key, str) and hasattr(self, key):
			return getattr(self, key)
		else:
			raise KeyError(key)

	def __setitem__(self, key: int | str, value: Any) -> None:
		if isinstance(key, tuple) and len(key) == 2:
			if all(isinstance(v, int) for v in key):
				self._data[key] = value
		elif isinstance(key, str) and hasattr(self, key):
			setattr(self, key, value)
		else:
			raise ValueError(key)

	def columns(self) -> "ColumnsView":
		if "columns" not in self._views:
			self._views["columns"] = ColumnsView(self)
		return self._views["columns"]

	def column(self, i: int) -> "Column":
		return self.columns()[i]

	def rows(self) -> "RowsView":
		if "rows" not in self._views:
			self._views["rows"] = RowsView(self)
		return self._views["rows"]

	def row(self, i: int) -> "Row":
		return self.rows()[i]
