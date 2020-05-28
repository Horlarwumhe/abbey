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
		self.assertEqual(ret,False)


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

