
# tokenize pattern into formatting elements so each one represents one index position
# get current character in data
# if current character in data matches current character in pattern, index data character +1
# else, index pattern character +1
# if current character in data matches current character in pattern, continue loop
# else, pattern match fails

# `?` escape formatting character to literal
# * any amt of any characters
# ? one of any character
# [abc] one of these characters
# (abc) any amt of these characters
# ! anti- prefix


def stringmatch(pattern: str, data: str, start: int = None, end: int = None) -> bool:
	data = data[start:end]
	current_data_idx = 0
	current_pattern_idx = 0
	
class StringPattern:
	def __init__(self, pattern: str):
		self.elements = []
		cur = ""
		for char in pattern:
			if char in ["*","?"]:
				self.elements.append(char)
			if char in ["!","`"]:
				if cur:
					self.elements.append(cur)
				cur = char
			elif char in ["[","("]:
				if not cur or cur in ["!","`"]:
					cur += char
			else:
				if cur.startswith("[","("):
					cur += char
				else:
					self.elements.append(char)
			if (cur.startswith("[") and cur.endswith("]")) or (cur.startswith("(") and cur.endswith(")")):
				self.elements.append(cur)
				cur = ""
		if cur:
			self.elements.append(cur)