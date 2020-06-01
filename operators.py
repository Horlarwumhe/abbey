# operator functions
# using this instead of operator in standard library
#to perform type conversion

def sqrt(x,y):
	try:
		return int(x) ** int(y)
	except (ValueError,TypeError):
		return 0
def add (x,y):
	try:
		return int(x) + int(y)
	except (ValueError,TypeError):
		try:
			return x + y
		except:
			return str(x) + str(y)

def sub(x,y):
	try:
		return int(x) - int(y)
	except (ValueError,TypeError):
		return 0

def mul(x,y):
	try:
		return int(x) * int(y)
	except (ValueError,TypeError):
		try:
			return x * y
		except:
			return 0

def lt(x,y):
	try:
		return x < y
	except (ValueError,TypeError):
		try:
			return int(x) < int(y)
		except (ValueError,TypeError):
			return str(x) < str(y)
def gt(x,y):
	try:
		return x > y
	except (ValueError,TypeError):
		try:
			return int(x) > int(y)
		except (ValueError,TypeError):
			return str(x) > str(y)
def le(x,y):
	try:
		return x <= y
	except (ValueError,TypeError):
		try:
			return int(x) <= int(y)
		except (ValueError,TypeError):
			return str(x) <= str(y)

def ge(x,y):
	try:
		return x >= y
	except (ValueError,TypeError):
		try:
			return int(x) >= int(y)
		except (ValueError,TypeError):
			return str(x) >= str(y)

def eq(x,y):
	return x == y


def ne(x,y):
	return x != y


def contains(x,y):
	if isinstance(y,(str,int)):
		return str(x) in str(y)
	else:
		return x in y
def truediv(x,y):
	try:
		return float(x) / float(y)
	except (ValueError,TypeError):
		return 0

def mod(x,y):
	try:
		return int(x) % int(y)
	except (ValueError,TypeError):
		return 0