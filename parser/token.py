from enum import Enum
from dataclasses import dataclass, field
from typing import Tuple
from fnmatch import fnmatch

class Markdown(Enum):
	CHECKBOX_FALSE = "- [ ] "
	CHECKBOX_TRUE = "- [x] "
	HEADER_1 = "# "
	HEADER_2 = "## "
	HEADER_3 = "### "
	HEADER_4 = "#### "
	HEADER_5 = "##### "
	HEADER_6 = "###### "

	@staticmethod
	def bullet(line) -> bool:
		return line.lstrip()[0] in "-*"

	@staticmethod
	def checkbox_true(line) -> bool:
		return line.lstrip()[:len(Markdown.CHECKBOX_TRUE)] == Markdown.CHECKBOX_TRUE

	@staticmethod
	def checkbox_false(line) -> bool:
		return line.lstrip()[:len(Markdown.CHECKBOX_FALSE)] == Markdown.CHECKBOX_FALSE

	@staticmethod
	def header(line) -> int:
		for header in (enum for enum in Markdown if enum.name.startswith("HEADER")):
			if line.lstrip().startswith(header.value):
				return header.value.count("#")

class YAML:
	INDENT_1 = "  "
	INDENT_2 = "    "

	@staticmethod
	def key_value(line):
		return fnmatch(str(line).strip(), f"*: *")

	@staticmethod
	def sequence_start(line):
		return fnmatch(str(line).strip(), f"*:\n")

	@staticmethod
	def sequence_item(line):
		line = str(line).strip()
		return fnmatch(line, INDENT_1 + "- *") or fnmatch(line, INDENT_2 + "- *")