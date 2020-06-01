from abbey.errors import LexerError


class Tokentype:

	def __init__(self,name, value, line, column):
		self.line = line
		self.column = column
		self.value = value
		self.name = name

	def __str__(self):
		return "('%s', '%s', %s, %s )"%(self.name,self.value,self.line,self.column)

	def __repr__(self):
		return str(self)


class LineLexer:

	def __init__(self,text,line_num):
		self.line_text = text
		self.line_num = line_num
		self.pos = 0
		self.current_char = self.line_text[self.pos]
		self.symbols = {
		")":"RPAREN",
		'(':"LPAREN",
		"{":'LCBRACK',
		'}':'RCBRACK',
		"[":'LBRACK',
		']':'RBRACK',
		':':"COLON",
		'?':"QUE",
		',':"COMMA"
		}
		self.keywords = {
        'try':"TRY",
        'func': 'FUNCTION',
        'return': 'RETURN',
        'else': 'ELSE',
        'elif': 'ELIF',
        'if': 'IF',
        'while': 'WHILE',
        'break': 'BREAK',
        'continue': 'CONTINUE',
        'for': 'FOR',
        'in': 'IN',
        'match': 'MATCH',
        'when': 'WHEN',
        'catch':"CATCH",
        'foreach':"FOREACH",
        'use':'USE',
        'as':"AS",
        'and':"AND",
        'or':"OR",
        'not':'NOT',
        'include':"INCLUDE",
        'class':"CLASS"
        # "FROM" :'from'
        }
		self.operators = {
	    '-':"-",
	    '+':'+',
	    '*':'*',
	    '/':'/',
	    "%":'%'
	    }


	def advance(self):
		self.pos += 1
		if self.pos > len(self.line_text) - 1:
			self.current_char = None
		else:
			self.current_char = self.line_text[self.pos]

	def name(self,column):

		result = ''
		while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
			self.column +=1
			column = self.column
			result += self.current_char
			self.advance()
			

		if result in self.keywords:
			name = self.keywords[result]
			return  Tokentype(name,result,self.line_num + 1,column)
		return Tokentype("NAME",result,self.line_num + 1,column)

	def string(self,column,kind=None):
		# "hhf"
		# kind --- double quote(") or single(')
		self.advance() #skip first "
		result = ""
		while self.current_char != kind:
			column = self.column
			if self.current_char is None:
				raise LexerError("unclosed string",self.line_num + 1,column)
			result += self.current_char
			self.advance()
			self.column +=1
		self.advance() # skip last "
		token = Tokentype("STRING",result,self.line_num + 1,column)
		return token

	def number(self,column):
		result =''
		while self.current_char is not None and self.current_char.isdigit():
			column = self.column
			result += self.current_char
			self.advance()
			if self.current_char == '.':
				if self.peek(1) == '.':
					#1...8
					pass
				else:
					result += '.'
					self.advance()
					while self.current_char is not None and self.current_char.isdigit():
						result += self.current_char
						self.advance()
					return Tokentype("NUMBER",float(result),self.line_num + 1,column)
			self.column +=1

		token = Tokentype("NUMBER",int(result),self.line_num + 1,column)
		return token

	def skip_whitespace(self):
		""" Skip all whitespaces between tokens from input """
		while self.current_char is not None and self.current_char.isspace():
			self.advance()
			self.column += 1
	def skip_comment(self):
		while self.current_char is not None:
			self.advance()
			self.column +=1

	def peek(self,pos):
		if self.pos + pos > len(self.line_text) - 1:
			return
		return self.line_text[self.pos +pos]

	def tokenize(self):
		found = []
		self.column = 0
		while self.current_char is not None:
			self.column += 1
			column = self.column
			if self.current_char.isspace():
				self.skip_whitespace()
				continue
			if self.current_char.isdigit():
				k = self.number(column)
				found.append(k)
				continue
			if self.current_char == '"':
				k = self.string(column,kind='"')
				found.append(k)
				continue
			if self.current_char == "'":
				k = self.string(column,kind="'")
				found.append(k)
				continue
			if self.current_char.isalpha() or self.current_char == "_":
				k = self.name(column)
				found.append(k)
				continue
			if self.current_char == "=":
				if self.peek(1) == "=":
					token = Tokentype("OPERATOR",'==',self.line_num + 1,column)
					found.append(token)
					self.advance()
					self.advance()
				elif self.peek(1) == ">": # forward arrow
					token = Tokentype("FOREACHOP",'=>',self.line_num + 1,column)
					found.append(token) 
					self.advance()
					self.advance()
				else:
					token = Tokentype("ASSIGN",'=',self.line_num + 1,column)
					found.append(token)
					self.advance()
				continue
			if self.current_char == ">":
				if self.peek(1) == "=":
					token = Tokentype("OPERATOR",'>=',self.line_num + 1,column)
					found.append(token)
					self.advance()
					self.advance()
				else:
					token = Tokentype("OPERATOR",'>',self.line_num + 1,column)
					found.append(token)
					self.advance()
				continue
			if self.current_char == '<':
				if self.peek(1) == "=":
					token = Tokentype("OPERATOR",'<=',self.line_num + 1,column)
					found.append(token)
					self.advance()
					self.advance()
				elif self.peek(1) == '>':
					token = Tokentype("OPERATOR",'<>',self.line_num + 1,column)
					found.append(token)
					self.advance()
					self.advance()
				else:
					token = Tokentype("OPERATOR",'<',self.line_num + 1,column)
					found.append(token)
					self.advance()
				continue
			if self.current_char == '*' and self.peek(1) == "*":
				token = Tokentype("OPERATOR",'**',self.line_num + 1,column)
				self.advance()
				self.advance()
				found.append(token)
				continue
			if self.current_char in self.operators:
				token = Tokentype("OPERATOR",self.current_char,self.line_num + 1,column)
				found.append(token)
				self.advance()
				continue
			if self.current_char in self.symbols:
				token = Tokentype(self.symbols[self.current_char],self.current_char,self.line_num + 1,column)
				found.append(token)
				self.advance()
				continue
			if self.current_char == "#":
				self.skip_comment()
				continue
			if self.current_char == '.':
				if self.peek(1) == '.' and self.peek(2) == '.':
					token = Tokentype("OPERATOR","...",self.line_num + 1,column)
					found.append(token)
					self.advance()
					self.advance()
					self.advance()
				else:
					t  = Tokentype("DOT",'.',self.line_num + 1,column)
					found.append(t)
					self.advance()
				continue
			else:
				raise LexerError('invalid character "{}"'.format(self.current_char),self.line_num + 1,column)
		return found

class Lexer:

	def __init__(self,s):
		self.text = s
		self.source_lines = []

	def tokenize(self):
		tokens = []
		last_indent = 0
		code = self.text
		indent_rule =None
		for line_num,line_code in enumerate(code.splitlines()):
		    if len(line_code) == 0 or line_code.isspace():
		    	self.source_lines.append('')
		    	continue
		    self.source_lines.append(line_code)
		    space = self.count_indent(line_code)
		    if indent_rule is None or indent_rule == 0:
		    	indent_rule = space
		    line_code = line_code[space:]  # remove trailing whitespace
		    line_tokens = LineLexer(line_code,line_num).tokenize()
		    if not line_tokens:
		    	#  no tokens, probably comment
		    	continue
		    if space > last_indent:
		    	token = Tokentype("INDENT",None,line_num+1,0)
		    	tokens.append(token)
		    elif space < last_indent:
		    	level = int((last_indent - space)/indent_rule)
		    	token = [Tokentype("DEDENT",None,line_num+1,0)] *level
		    	tokens.extend(token)
		    last_indent = space
		    if space == 0:
		    	indent_rule = 0
		    tokens.extend(line_tokens)
		    tokens.append(Tokentype("NEWLINE",None,line_num+1,0))
		    c = ' '*space
		    c += line_code
		if last_indent > 0:
			level = int(last_indent/indent_rule)
			token = [Tokentype("DEDENT",None,line_num+1,0)] * level
			tokens.extend(token)
		return tokens

	def count_indent(self,s):
		h = 0
		if s[0] in [' ','\t']:
			for c in s:
				if c not in [' ','\t']:
					break
				h += 1
		return h

