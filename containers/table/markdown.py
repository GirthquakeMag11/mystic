from . import Table
import typing as T

class MarkdownTable(Table):

	def __init__(self, initial_data = None, **settings):
		super().__init__(initial_data)
		self._settings = {**settings}
		self._stats = {}

	def show_headers(setting: bool | T.Optional = True):
		self._settings["show_headers"] = setting

	def hide_headers(setting: bool | T.Optional = True):
		self.show_headers(not setting)

	def pad_cells(setting: int = 1):
		self._settings["cell_padding"] = int(setting) if setting else 0

	def column_widths(self):
		for col in self.columns():
			width = 0
			for cell in col:
				if len(str(cell.value)) > width:
					width = len(str(cell.value))
			if self._settings.get("show_headers", False):
				if len(col.title) > width:
					width = len(col.title)
			col.metadata(width = width)
		