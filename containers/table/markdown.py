from . import Table
import typing as T

class MarkdownTable(Table):

	# # #

	class LineBuilder:

		def initialize(self):
			self.widths = (w for w in self.table.column_widths())
			self.current_line = []
			self.lines = []
			self.progress = 0
			return self

		def __init__(self, table):
			self.table = table
			self.initialize()

		def __iter__(self):
			return self.initialize()

		@property
		def total_columns(self):
			return len(self.widths)

		@property
		def column(self):
			return len(self.current_line)

		@property
		def row(self):
			return len(self.lines) if not self.table.showing_titles else len(self.lines) - 1

		def cell_text(self, cell = None, data = "", justify = "left"):
			value = str(cell.value) if cell is not None else data
			justification = {"left":value.ljust, "right":value.rjust, "center":value.center}
			justified_vale = f"{just(width=self.widths[self.column], fillchar=" ")}"
			padded_value = f"|{value.center(width=(self.widths[self.column] + (2 * self.table.cell_padding)), fillchar=" ")}|" 
			return padded_value

		def progress_line(self):
			self.lines.append("\n" + "".join([element for element in MarkdownTable.adjoin(self.current_line)]))
			self.current_line = []
			self.progress += 1
			return self.lines[-1]

		def column_title_line(self):
			lambda data: self.cell_text(data=data)
			line = [self.cell_text()]
			for col in self.table.columns():
				line.append(data(data=col.title))
			joined = "".join([part for part in MarkdownTable.adjoin()])
			self.lines.append("\n" + joined)
			return self.lines[-1]

		def __next__(self):
			if self.table.showing_titles and len(self.lines) < 1:
				return self.column_title_line()
			while self.column <= self.total_columns:
				self.current_line.append(
					self.cell_text(
						cell=self.table.cell(column=self.column, row=self.row)
						)
					)
			if self.current_line:
				if self.table.showing_titles:
					self.current_line.insert(0, self.cell_text(data=self.table.rows()[self.row].title))
				return self.progress_line()
			if self.progress >= len(self.table.rows()):
				raise StopIteration

	# # #

	def __init__(self, initial_data = None, **settings):
		super().__init__(initial_data)
		self._settings = {**settings}
		self._builder = MarkdownTable.LineBuilder(self)
		self._stats = {}

	def __iter__(self):
		yield from self._builder

	# # #

	@property
	def showing_titles(self):
		return bool(self._settings.get("show_titles", False))

	@property
	def cell_padding(self):
		return int(self._settings.get("cell_padding", 1))

	# # #

	def show_titles(setting: bool | T.Optional = True):
		self._settings["show_titles"] = setting

	def hide_titles(setting: bool | T.Optional = True):
		self.show_titles(not setting)

	def pad_cells(setting: int = 1):
		self._settings["cell_padding"] = int(setting) if setting else 0

	def column_widths(self) -> T.Iterable[int]:
		if self.showing_titles:
			yield self.row_title_width()
		for col in self.columns():
			cur_width = 0
			for cell in col:
				width = len(str(cell.value))
				title_width = len(col.title) if self.showing_titles else 0
				cur_width = [cur_width, width, title_width].sort()[-1]
			col.metadata(width = cur_width)
			yield cur_width

	def row_title_width(self) -> int:
		cur_width = 0
		if self.showing_titles:
			for row in self.rows():
				width = len(row.title) + (2 * self.cell_padding)
				if width > cur_width:
					cur_width = width
		return cur_width

	# # #

	@staticmethod
	def adjoin(*strings):
		current = ""
		while strings:
			if not current:
				current = strings.pop(0)
			if not strings:
				break
			if current[-1] == strings[0][0]:
				current += strings.pop(0)[1:]
				continue
			else:
				yield current
				current = ""
				continue

		yield current
