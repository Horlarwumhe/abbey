import argparse
import sys
import os
import traceback
sys.path.append(os.path.dirname(os.getcwd()))


from abbey import Interpreter
from abbey import Lexer
from abbey import Tokens
from abbey import Parser , Programs
from abbey.utils import Environment
from abbey.utils import report_syntax_error , report_error
from abbey.errors import *

def create_argparse():
	parser = argparse.ArgumentParser(description='abbey lang main program')
	parser.add_argument('file',)
	parser.add_argument('-d','--debug',default=False)
	args = parser.parse_args()
	return args



env = Environment()
def main():
	args = create_argparse()
	path = os.path.dirname(args.file)
	try:
		file = open(args.file).read()
	except:
		print('file not found',args.file)
		return
	lexer = Lexer(file)
	try:
		tokens = lexer.tokenize()
	except AbbeySyntaxError as err:
		if args.debug:
			traceback.print_exc(file=sys.stdout)
		else:
			report_syntax_error(lexer, err)
		return
	token_stream = Tokens(tokens)
	try:
		program = Parser().parse_all(token_stream)
		# print(program)
	except AbbeySyntaxError as err:
		if args.debug:
			traceback.print_exc(file=sys.stdout)
			return
		report_syntax_error(lexer, err)
		return

	code = Interpreter(program,path)
	code.create_env(env)

	try:
	     pv = code.interpret()
	except AbbeyError as e:
		if args.debug:
			traceback.print_exc(file=sys.stdout)
			return
		report_error(lexer,e)
		return
	except AbbeyModuleError as err:
		report_error (err,err)


def test():
        code = input('>>># ')
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        token_stream = Tokens(tokens)
        program = Parser().parse_all(token_stream)
        code = Interpreter(program)
        code.create_env(env)
        return code.interpret()
main()
        
