import json,sys

def get_item():
	return { "a": 5, "b": 10 }

def get_array():
	results = []
	yield "["
	for x in xrange(5):
		if x > 0:
			yield ","
		yield json.dumps(get_item())
	yield "]"

if __name__ == "__main__":
	for s in get_array():
		sys.stdout.write(s)
	sys.stdout.write("\n")