from tkinter import (
	ttk,
	filedialog,
	colorchooser,
	messagebox,
	)
import tkinter as tk
import threading
import functools


class Dialog:

	@staticmethod
	def open_filename():
		return filedialog.askopenfilename()

	@staticmethod
	def save_filename():
		return filedialog.asksavefilename()

	@staticmethod
	def ask_directory():
		return filedialog.askdirectory()

	@staticmethod
	def color_chooser():
		return colorchooser.askcolor()

	@staticmethod
	def message_box():
		return messagebox.showinfo()


class Window(tk.Toplevel):

	def __init__(self, parent = None):
		self.parent = parent if parent is not None else Root()
		super().__init__(self.parent)
		if isinstance(self.parent, Root):
			self.parent.children[id(self)] = self
			self.protocol("WM_DELETE_WINDOW", functools.partial(self.parent.destroy_window, id(self)))

	def __gt__(self, other):
		return bool(Root().call("wm", "stackorder", str(self), "isabove", str(other)) == "1")

	def __lt__(self, other):
		return bool(Root().call("wm", "stackorder", str(self), "isbelow", str(other)) == "1")

class Root(tk.Tk):
	INSTANCE = None
	THREADLOCK = threading.Lock()
	def __new__(cls):
		if not isinstance(cls.INSTANCE, cls):
			cls.INSTANCE = cls()
		return cls.INSTANCE
	def __init__(self):
		if type(self).INSTANCE is self and not hasattr(self, "_init"):
			self._init = True
			super().__init__()
			self.option_add("*tearOff", False)
			self.withdraw()
			self.children = {}

	@classmethod
	def destroy_window(cls, window_id):
		if window_id in cls().children:
			cls().children.pop(window_id).destroy()
		if not cls().children:
			cls().destroy()

	@classmethod
	def rel_geometry(cls, percentage):
		with cls.THREADLOCK:
			return f"{int(cls().winfo_screenwidth()) * percentage}x{int(cls().winfo_screenheight() * percentage)}"

	@classmethod
	def safe_update(cls):
		with cls.THREADLOCK:
			cls().update_idletasks()

	@classmethod
	def update(cls):
		with cls.THREADLOCK:
			cls().update()