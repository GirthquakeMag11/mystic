import string

def textparse(data: str, deduplicate = False, omit_whitespace = False, attempt_urls = True, attempt_emojis = True):
	GROUPING_CHARS = ("'","’", *string.ascii_letters, *string.digits)
	COMPOUND_CHARS = (".","-","–","—","@",",","/","_",":")

	idx = -1
	cur_token = ""
	seen = set()
	queued_tokens = []

	def cur_char():
		if data.strip() and idx > -1:
			return data[idx]

	def next_chars(cont_char = None, stop_idx = None):
		if stop_idx:
			return data[idx:idx + stop_idx]
		elif cont_char:
			i = 0
			while data[idx + i] == cont_char:
				i += 1
			return next_chars(stop_idx=i+1)

	def to_char(stop_char = None, stop_idx = None):
		if stop_idx:
			if len(data) > stop_idx + 1:
				return data[idx:stop_idx + 1]
			elif len(data) <= idx + 1:
				return data[idx:]
		elif stop_char:
			if (char_idx := data.find(stop_char, idx + 1)) > 0:
				return to_char(stop_idx=char_idx)
			else:
				return ""

	def queue_check(token):
		nonlocal seen
		if omit_whitespace and (not token.strip()):
			return False
		if deduplicate:
			if token in seen:
				return False
			else:
				seen.add(token)
		return token

	def queue_current():
		nonlocal cur_token
		nonlocal queued_tokens
		if queue_check(cur_token):
			queued_tokens.extend(cur_token)
			cur_token = ""

	def queue(*tokens):
		nonlocal queued_tokens
		queue_current()
		queued_tokens.extend([t for t in tokens if queue_check(t)])

	def group_char():
		nonlocal cur_token
		if cur_char() in GROUPING_CHARS:
			cur_token += cur_char()
			return True
		return False

	def compound_char():
		return cur_char() in COMPOUND_CHARS

	def special_compound():
		nonlocal idx
		nonlocal cur_token
		if cur_char() == ".":
			if next_chars(stop_idx=3) == "...":
				queue("...")
				idx += 2
				return True

		elif cur_char() == ":":
			if attempt_emojis:
				to_next_colon = to_char(stop_char=":")
				if to_next_colon.strip() and not any(char in string.whitespace for char in to_next_colon):
					queue(to_next_colon)
					idx += len(to_next_colon) + 1
					return True
			if attempt_urls:
				if cur_token.strip().casefold().startswith("http"):
					cur_token += ":"
					return True

	def standard_compound():
		try:
			before = data[idx - 1] in GROUPING_CHARS
		except IndexError:
			before = True
		try:
			after = data[idx + 1] in GROUPING_CHARS
		except IndexError:
			after = False
		return bool(before and after)

	def shift_idx():
		nonlocal idx
		if len(data) - 1 >= idx + 1:
			idx += 1
			return True
		return False

	while True:
		if queued_tokens:
			yield queued_tokens.pop(0)
			continue

		if shift_idx():
			if group_char():
				continue
			if compound_char():
				if special_compound():
					continue
				if standard_compound():
					continue
			queue(cur_char())

		elif cur_token:
			queue_current()

		else:
			break