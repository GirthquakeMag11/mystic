from tkinter import ttk
import tkinter as tk
import threading
import functools

class Window(tk.Toplevel):
	def __init__(self, root, **params):
		super().__init__(root)
		self.threadlock = threading.Lock()
		self.root = root
		self.protocol("WM_DELETE_WINDOW", functools.partial(self.root.destroy_window, id(self)))
		self.title_var = tk.StringVar(value=params.pop("title", "Window"))
		self.width_var = tk.IntVar(value=params.pop("width", 300))
		self.height_var = tk.IntVar(value=params.pop("height", 300))
		self.last_width = 0
		self.last_height = 0

	def _update(self, event):
		with self.threadlock:
			def _geometry():
				super().geometry(f"{self.width}x{self.height}")
				self.last_height = self.height
				self.last_width = self.width

			if event in ("geometry", "all"):
				if self.width != self.last_width or self.height != self.last_height:
					_geometry()

		self.root.update_idletasks()

	@height.setter
	def height(self, value: int):
		self.height_var.set(int(value))
		self._update("geometry")

	@property
	def height(self):
		return self.height_var.get()

	@width.setter
	def width(self, value: int):
		self.width_var.set(int(value))
		self._update("geometry")

	@property
	def width(self):
		return self.width_var.get()

	@title.setter
	def title(self, value: str):
		self.title_var.set(str(value))
		super().title(value)

	@property
	def title(self):
		return self.title_var.get()

class Root(tk.Tk):
	INSTANCE = None
	def __init__(self):
		if Root.INSTANCE is None:
			Root.INSTANCE = self
			super().__init__()
			self.withdraw()
			self.option_add("*tearOff", False)
			self.windows = {}
			self.threadlock = threading.Lock()

	def create_window(self, **params):
		with self.threadlock:
			window = Window(self, **params)
			self.windows[id(window)] = window

	def destroy_window(self, window_id):
		with self.threadlock:
			if window := self.windows.pop(window_id, None):
				window.destroy()
