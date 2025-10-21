import string
from typing import Any, Sequence

def indexalpha(data: str) -> int:
	if not isinstance(data, str):
		if not hasattr(data, "__str__"):
			raise TypeError(f"'data' argument must be a string. Received type: {type(char).__name__}")
		data = str(data)
	if len(data) > 1:
		return (indexalpha(c) for c in data)
	if data in string.ascii_letters:
		return ord(data) - ord("A" if data.isupper() else "a")
	else:
		return -1

def mean(*args: Any):
	return sum(args) / len(args)

def median(*args: Any):
	return sorted(args)[len(args) // 2]

def mode(*args: Any):
	m = (0, None)
	for a in args:
		if (c := args.count(a)) > m[0]:
			m = (c, a)
	return m[1]

def percentof(part, whole):
	return (part / whole) * 100

def roundup(arg: float):
	return arg + (1 - (arg % 1))

def rounddown(arg: float):
	return arg - (arg % 1)

def round(arg: float):
	if (rem := arg % 1) > 0.5:
		return roundup(arg)
	elif rem < 0.5:
		return rounddown(arg)
	elif rem == 0.5:
		raise ValueError(rem)

def normalize_to_one(arg: Any, max_val: Any, min_val: Any = 0):
	return (arg - min_val) / (max_val - min_val)

def normalize_to_range(value, value_range: Sequence, new_range: Sequence):
	nr = sorted(new_range)
	vr = sorted(value_range)
	return nr[len(vr) * ((value - vr[0]) // (vr[-1] - vr[0]))]