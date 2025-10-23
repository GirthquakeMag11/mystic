from abc import ABC, abstractmethod
import typing as T
from collections.abc import (
	Iterable,
	MappingView,
	MutableMapping,
	MutableSequence,
	Sequence,
	)
import string
from dataclasses import dataclass
import warnings


class Table(MutableMapping):

	# # #

	class TableElement(ABC):

		def __init_subclass__(cls):
			super().__init_subclass__(cls)
			if not hasattr(cls, "__str__"):
				warnings.warn(f"TableElement subclass {cls.__name__} missing '__str__' method, metadata storage non-functional.", UserWarning)

		def metadata(self, **values):
			if not hasattr(self, "__str__"):
				warnings.warn(f"TableElement subclass {cls.__name__} missing '__str__' method, metadata storage non-functional.", UserWarning)
				return
			if str(self) not in self.table._metadata:
				return self.table._metadata.setdefault(str(self), dict(values))
			self.table._metadata[str(self)].update(dict(values))
			return self.table._metadata[str(self)]

		@abstractmethod
		def __str__(self):
			pass

	# # #

	@dataclass(frozen=True)
	class Cell(TableElement):
		table: "Table"
		column: int
		row: int
		value: T.Any

		def set(self, value: T.Any) -> "Table.Cell":
			object.__setattr__(self, "value", value)
			return self

		def __post_init__(self):
			if isinstance(self.value, Table.Cell):
				object.__setattr__(self, "value", self.value.value)

		def __str__(self):
			return f"{type(self).__name__}_{self.column}x{self.row}"

	# # #

	class TableSubset(ABC, TableElement):

		def __init_subclass__(cls, *args, **kwargs):
			super().__init_subclass__(cls)
			abstract_methods = ("__getitem__","__setitem__","__len__")
			for mandatory in abstract_methods:
				if not callable(getattr(cls, mandatory, None)):
					raise TypeError(f"TableSubset subclass {cls.__name__} missing required method {mandatory}.")

		def __init__(self, table: "Table", table_index: int, initial_data: T.Iterable = None):
			self.table = table
			self.idx = int(table_idx)
			if self.idx > getattr(self.table, f"_last_{type(self).__name__}", -1):
				setattr(self.table, f"_last_{type(self).__name__}", self.idx)
			if initial_data and hasattr(initial_data, "__iter__"):
				for i, v in enumerate(initial_data):
					self[i] = v

		def __iter__(self) -> T.Iterable[T.Any]:
			for idx in range(len(self)):
				yield self[idx]

		@abstractmethod
		def __getitem__(self, idx):
			pass

		@abstractmethod
		def __setitem__(self, idx, item):
			pass

		@abstractmethod
		def __len__(self):
			pass

	# # #

	class Column(TableSubset):

		def __getitem__(self, idx: int) -> T.Any:
			return self.table.cell(self.idx, idx)

		def __setitem__(self, idx: int, item: T.Any):
			self.table.cell(self.idx, idx).set(item)

		def __len__(self) -> int:
			return getattr(self.table, "_last_row", -1) + 1

	# # #

	class Row(TableSubset):

		def __getitem__(self, idx: int) -> T.Any:
			return self.table.cell(idx, self.idx)

		def __setitem__(self, idx: int) -> T.Any:
			self.table.cell(idx, self.idx).set(item)

		def __len__(self) -> int:
			return getattr(self.table, "_last_column", -1) + 1

	# # #

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
			if idx > 0:
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

	# # #

	class ColumsView(TableView):

		def subset_factory(self, idx: int) -> "Table.TableSubset":
			return Table.Column(self.table, idx)

		def __len__(self) -> int:
			return getattr(self.table, "_last_column", -1) + 1

	# # #

	class RowsView(TableView):

		def subset_factory(self, idx: int) -> "Table.TableSubset":
			return Table.Row(self.table, idx)

		def __len__(self) -> int:
			return getattr(self.table, "_last_row", -1) + 1

	# # #

	@classmethod
	def columnsview(cls, table: "Table") -> "Table.ColumnsView":
		return cls.ColumnsView(table)

	@classmethod
	def rowsview(cls, table: "Table") -> "Table.RowsView":
		return cls.RowsView(table)

	def __init__(self, initial_data = None):
		self._data = {}
		self._metadata = {}
		self._views = {}

		if isinstance(initial_data, type(self)):
			self.__dict__.update(getattr(initial_data, "__dict__"))

	def cell(self, column: int, row: int, default: T.Any = None) -> "Table.Cell":
		return self._data.setdefault((int(column), int(row)), Table.Cell(self, int(column), int(row), default))

	def column(self, index: int, default: T.Iterable = None) -> "Table.Column":
		col = self.columns()[int(index)]
		if default:
			for i, v in enumerate(default):
				if not col[i]:
					col[i] = v
		return col

	def row(self, index: int, default: T.Iterable = None) -> "Table.Row":
		row = self.rows()[int(index)]
		if default:
			for i, v in enumerate(default):
				if not row[i]:
					row[i] = v
		return row

	def columns(self) -> "Table.TableView":
		if "columns" not in self._views:
			self._views["columns"] = type(self).columnsview(self)
		return self._views["columns"]

	def rows(self) -> "Table.TableView":
		if "rows" not in self._views:
			self._views["rows"] = type(self).rowsview(self)
		return self._views["rows"]

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