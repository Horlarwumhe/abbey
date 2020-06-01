import sys ,os

sys.path.append(os.path.dirname(os.getcwd()))

from abbey.lexer import Lexer 
from abbey.tokens import  Tokens
from abbey.parser import Parser , Programs
from abbey.interpreter import Interpreter

import unittest


class Test:

	def parse(self,code):
		l = Lexer(code).tokenize()
		t = Tokens(l)
		p = Parser()
		prog = p.parse_all(t)
		interpreter = Interpreter(prog)
		interpreter.create_env()
		return interpreter.interpret()

class BoolOperatorTest(Test,unittest.TestCase):
	#test boolean operators , and , or in 


	def test_bool(self):
		code ="""8 > 5 and 5 < 7"""
		ret = self.parse(code)
		self.assertEqual(ret,True)

		code = """6 == 6 and 7 <> 7"""
		ret = self.parse(code)
		code = """not 'j' in {j:'play',p:'ghsd'}"""
		r = self.parse(code)
		self.assertEqual(ret,False)
		self.assertEqual(r,False)


class Testassign(Test,unittest.TestCase):

	def test_assign(self):
		code = """
name = 'myname'
name
"""
		ret = self.parse(code)
		self.assertEqual(ret,'myname')

class Testreturn(Test,unittest.TestCase):

	def test_return(self):
		c = """
func calc(num1,num2,div=8):
    r = num1 + num2
    return r/div
calc(67,33)"""
		ret = self.parse(c)
		self.assertEqual(ret,12.5)

class ClassTest(Test,unittest.TestCase):
	def test_class(self):

		code ="""
class Calc(num1,num2):
	this.num1 = num1
	this.num2 = num2
	this.result = []

	func add():
		this.result.append(this.num1 + this.num2)
		return this.num1 + this.num2
	func sub():
		this.result.append(this.num1 - this.num2)
		return this.num1 - this.num2
	func div(by):
		d = this.add()
		this.result.append(d/by)
		return d/by
	func all():
		return this.result
c = Calc(56,34)
c.add()
c.sub()
7 - 78
c.div(6)
c.all()
	"""
		ret = self.parse(code)
		self.assertEqual(ret,[90,22,90,15.0])

if __name__ == '__main__':
	unittest.main()