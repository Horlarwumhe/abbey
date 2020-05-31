from abbey.lexer import Lexer
from abbey.parser import Parser , Programs
from abbey.tokens import Tokens
from abbey.utils import Environment as Env
def prepare_module(file,name,self):
	# self, = Interpreter
	try:
		code = open(file).read()
	except Exception:
		raise ImportError('module not found')
	l = Lexer(code).tokenize()
	t = Tokens(l)
	p = Parser().parse_all(t)
	ast = Programs(p)
	func = ast.function
	for node in ast.programs:
		if node._name == 'assign':
			# set all assignment to env
			self.visit_assignment(node,self.env)
		if node._name == "function":
			if node.name == name:
				continue # function beign imported
			else:
				self.env.set(node.name,node)
		# if node has body,e.g if,try,match, visit the body and set all assign to env
		body_name = ''
		if hasattr(node,'body'):
			body_name = 'body'
		elif hasattr(node,'if_body'):
			body_name = 'if_body'
		elif hasattr(node,'else_body'):
			body_name = 'else_body'
		set_body(node,body_name,self)
	if func:
		for f in func:
			if f.name == name:
				return f


def set_body(node,body_name,self):
	body = getattr(node,body_name,None)
	if body is None:
		return
	for n in body:
		if n._name == 'assign':
			self.visit_assignment(n,self.env)


def prepare_module(code,self):
	# self, = Interpreter
	l = Lexer(code).tokenize()
	t = Tokens(l)
	p = Parser().parse_all(t)
	ast = Programs(p)
	env = Env()
	self.programs = p
	self.create_env(env)
	self.interpret()
	return env

def load_module(module,self):
	return prepare_module(module,self)
