from typing import Any, Sequence
from random import choice as random_choice

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
		return random_choice([roundup(arg), rounddown(arg)])

def normalize_to_one(arg: Any, max_val: Any, min_val: Any = 0):
	return (arg - min_val) / (max_val - min_val)

def normalize_to_range(value, value_range: Sequence, new_range: Sequence):
	nr = sorted(new_range)
	vr = sorted(value_range)
	return nr[len(vr) * ((value - vr[0]) // (vr[-1] - vr[0]))]

if __name__ == "__main__":
	"""
	Starting value of 1, each iteration adds 1
	logs, in percentage, how much each iteraction the value
	has increased by overall with that iteration
	"""
	end = input("stop val  ")

	log = []
	a, b = 1, 2
	while b <= int(end) + 1:
		log.append(percentof(b, a) - 100)
		a, b = b, b + 1
	for idx, val in enumerate(log, start=1):
		print(f"{idx}".ljust(5) + f"+{val:.2f}%".rjust(5))