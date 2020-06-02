from  abbey.errors import TypeError_


class Str(str):

	def length(self):
		return len(self)

	def lenght(self):
		#spelling issue
		return len(self)

def SquareRoot(self,x,y):
	return x**y

def prints(self,*args):
	print(*args)

def opens(self,*args):
	return open(*args)

def _len(self,obj):
	if isinstance(obj,int):
		return len(str(obj))
	return len(obj)

def _slice(self,obj,start,stop):
	new = obj[start:stop]
	return new

class Builtins:
	# param_num = None
	# name = ''
	# callback = ''
	# overide attributes
	def __init__(self,params=None,keywords=None,body=None,line=None):
		self.params = params

	def check_args(self,node):
		if self.param_num == "*":
			return 
		if len(node.arguements) != self.param_num:
			given = len(node.arguements)
			raise TypeError_('builtin function {}() takes {} positional argument but {} were given '.format(self.name,self.param_num,given),node.line)

class Open(Builtins):
	name = 'open'
	param_num = '*'
	callback = opens

class Write(Builtins):
	name = 'write'
	param_num = '*'
	callback = print

class Square(Builtins):
	name = 'sqrt'
	param_num = '*'
	callback = SquareRoot

class Print(Write):
	name = 'print'

class Len(Builtins):
	name = 'len'
	param_num = 1
	callback = _len
class Int(Builtins):
	name = 'int'
	param_num = 1
	callback = int

class Slice(Builtins):
	name = 'slice'
	param_num = 3
	callback = _slice

class Input(Builtins):
	name = 'input'
	param_num ='*'
	callback = input
builtins = [Write,Open,Square,Len,Int,Input,Slice]
def load_builtins(env):
	for kls in builtins:
		env.set(kls.name,kls())

