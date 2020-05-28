import sys ,os

sys.path.append(os.path.dirname(os.getcwd()))

from abbey.lexer import Lexer 
from abbey.tokens import  Tokens
from abbey.parser import Parser , Programs

import unittest
code="""

func greet(name,times=5,user="now"):
    return name
func count(end=10):
    return end
greet(name)
lang = 'python'
print(lang)
count(10)
"""


class FunctionTests(unittest.TestCase):

	def parse(self,code):
		l = Lexer(code).tokenize()
		t = Tokens(l)
		p = Parser()
		prog = p.parse_all(t)
		return Programs(prog)


	def test_Function(self):
		c = """
func greet(name,user,times=10):
    i = 0
    while i > times:
        print(user)
        print(name)
        i = i + 1
func add(k,u):
    return k + u
		"""
		parse = self.parse(c)
		functions = parse.function
		fun_names = [functions[0].name,functions[1].name]

		self.assertEqual(['greet','add'],fun_names)

		self.assertEqual(len(functions),2)

		func1 = functions[0] # first function
		self.assertEqual(func1.name,'greet')

		func2 = functions[1]   
		self.assertEqual(func2.name,'add')

		#parameters 
		self.assertEqual(['name','user'],func1.params)

		#keywords
		keywords = {k:v.value for k,v in func1.keywords.items()}
		self.assertEqual({'times':10},keywords)

	def test_function_call(self):
		c = """
print('hello')
len(746434)"""
		parse = self.parse(c)
		# implement via getattr which call get_program(name)
		calls = parse.call

		self.assertEqual(len(calls),2)

		calls_name = [calls[0].name,calls[1].name]
		self.assertEqual(['print','len'],calls_name)
		# call args
		self.assertEqual(calls[0].arguements[0].value,'hello')
		self.assertEqual(calls[1].arguements[0].value,746434)

class AssignmentTest(unittest.TestCase):
	def parse(self,code):
		l = Lexer(code).tokenize()
		t = Tokens(l)
		p = Parser()
		prog = p.parse_all(t)
		return Programs(prog)

	def test_Assignment(self):
		c = '''
date = "today" ? "nb" in "khj" : "yesterday"
score = 87'''

		assign = self.parse(c).get_program("assign")
		self.assertEqual(len(assign),2)

		
		# second assignment
		first = assign[1]
		self.assertEqual(first.left.value,'score')
		self.assertEqual(first.right.value,87)

		# first assignment , conditional assignment
		second = assign[0]
		self.assertEqual(second.left.value,'date')
		self.assertEqual(second.right.value,'today')
		self.assertEqual(second.right2.value,'yesterday')
		self.assertEqual(second.test.operator,'in')

class IfTest(unittest.TestCase):

	def parse(self,code):
		l = Lexer(code).tokenize()
		t = Tokens(l)
		p = Parser()
		prog = p.parse_all(t)
		return Programs(prog)

	def test_if(self):
		c = """
if 'go' == 'Go':
	print('yes')
elif 'ko' == 'ki':
	print('other')
elif 8 > 9:
	print('third')
elif 8 < 6:
	print('fourth')

		"""
		if_ = self.parse(c).if_ #self.parse(c).get_program('if')

		
		if_ = if_[0]
		# 3 elif conditions
		elifs = if_.elifs
		self.assertEqual(3,len(elifs))
		self.assertEqual('==',if_.test.operator)
		# no else body, assert it is None
		self.assertEqual(if_.else_body,None)

if __name__ == '__main__':
	unittest.main()
