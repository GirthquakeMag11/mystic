from .text_parse import parse

def pattern(data: str):

	highest_int = 0

	def normalize_to_range(value, value_range, target_range):
		value_range = sorted(value_range)
		target_range = sorted(target_range)
