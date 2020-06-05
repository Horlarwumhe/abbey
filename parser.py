from abbey import ast
from abbey.errors import ParserError, LexerError
from abbey.utils import assert_expression


statements = {
            'FUNCTION': "function",
            'IF': 'if',
            'MATCH': 'match',
            'WHILE':"while",
            'FOR': 'for',
            'RETURN': "return",
            'BREAK': 'break',
            'CONTINUE': 'continue',
            "ELIF":'elif',
            'ELSE':'else',
            'CATCH':"catch",
            "TRY":'try',
            "USE":'use',
            'AS':'as',
            'IN':'in',
             'OR':'or',
             'AND':'and',
             'INCLUDE':'include',
             'CLASS':'class',
            }
expression =  {'NUMBER':"num" ,
              'STRING': "str",
              'NAME': "identifier",
              #'LPAREN': "group",
              'LBRACK': "array",
              'LCBRACK': "dict",
              #'OPERATOR': "unary",
              'COMMA':'err',
              'NOT':'not',
              'OPERATOR':'math'
              }
infix = {
    'OPERATOR': "compare",
    'LPAREN': "call",
    'LBRACK': 'subscript',
    "DOT" : "attr",
    'IN':'logical',
    "OR":'logical',
    "AND":'logical'
}


precedence = {
# higher precendence means evaluate lower precendent first
# a > b and a == 8;
# a + 3 * 6 , eval * first
    "and":6,
    "or":5,
    "in":5,
    '>': 4,
    '>=': 4,
    '<': 4,
    '<=': 4,
    '==':4,
    "+":3,
    '-':3,
    "*":2, #times first
    
}

class BaseParser:
    
    def get_precedence(self,token):
        p = precedence.get(token.value,-1)
        return p


class Expression(BaseParser):

    def __init__(self):
        self.depend = ["else","elif","catch",'in','as','or','and']
        self.keywords = ['as','in','use','and','or']
        self.scope = []
        

    def parse(self,tokens,each =False):
        statements = []
        while not tokens.seen_all:
            parser_func =  self.get_statement_paser(tokens.current.name,tokens)
            ret = parser_func(tokens)
            if ret is not None:
                statements.append(ret)
            else:
                break
        return statements

    def get_statement_paser(self,name,tokens=None):
        '''get function to parse a token'''
        parser = statements.get(name)
        if parser is None:
            return self.check_expression
        print(name.lower())
        if name.lower() in self.depend:
            if name.lower() in ['else','elif']:
                raise ParserError(f'{name} condition outside if condition',tokens.current)
            elif name.lower() in ( 'in','as','and','or'):
                raise ParserError('Syntax error, can"t assign to keyword. "%s" is keyword'%name.lower(),tokens.current)
            raise ParserError(f'{name} statement without try block',tokens.current)
        func = 'parse_%s_statement'%parser
        fun_name = getattr(self,func,None)
        assert fun_name is not None, "Parser has no function for '%s' statement"%parser
        return fun_name

    def err_expression(self,tokens):
        raise ParserError("SyntaxError: unexpected tokens",tokens.current)

    def get_expression_parser(self,name):
        '''get function to parse an expression'''
        fun =  expression.get(name)
        if fun is None:
            return
        return getattr(self,'%s_expression'%fun)

    def get_infix_parser(self, name):

        fun = infix.get(name)
        if fun is None:
            return
        return getattr(self,'%s_expression'%fun)

    def check_expression(self,tokens,each=False):

        line_num = tokens.current.line
        exp = self.parse_expression(tokens)
        if exp is not None:
            if tokens.is_end():
                return exp
            if tokens.now.name == 'ASSIGN':
                left = exp
                return self.assignment_expression(tokens, left)
            elif  tokens.current.name == 'COMMA':
                others =  self.list_expression(tokens)
                left = exp
                left = [left] + others
                if tokens.now.name == 'ASSIGN':
                    return self.assignment_expression(tokens, left)
                
            if tokens.prev.name == "DEDENT":
                # there is one undetected bug now, use this to solve it
                pass
            else:
                self.eat(tokens,"NEWLINE")
            return exp


        if tokens.current.name == "INDENT":
            raise ParserError('unexpected indent',tokens.current)

    def parse_expression(self,tokens,pre=-1):

        parser = self.get_expression_parser(tokens.current.name)
        if not parser:
            return
        left = parser(tokens)
        while True:
            try:
                suffix = self.get_infix_parser(tokens.current.name)
            except ParserError:
                break
            if suffix:
                current_pre = self.get_precedence(tokens.current)
                if pre != -1:
                    if current_pre > 0 and current_pre > pre:
                        break
                ret = suffix(tokens,left)
                left = ret
            else:
                break
        return left

    def str_expression(self,tokens):

        token = self.eat(tokens,"STRING")
        return ast.String(token.value,token.line)

    def num_expression(self,tokens):

        token = self.eat(tokens,"NUMBER")
        return ast.Number(token.value,token.line)
    def math_expression(self,tokens):
        raise ParserError('this is not supported yet "-x or + x", use x - y instead',tokens.current)
        pass

    def assignment_expression(self,tokens, left):
        multiple = False
        if not isinstance(left,(ast.Identifier,ast.SubscriptOperator,ast.Objcall,list)):
            raise ParserError("SyntaxError: cant assign to %s"%left._name,tokens.current)
        self.eat(tokens,'ASSIGN')
        line_num = left[0].line if isinstance(left,list) else left.line
        test, right2 = None, None
        right = self.parse_expression(tokens)
        if not right:
            raise ParserError('SyntaxError: expected assignment value',tokens.current)
        if tokens.current.name == 'COMMA':
                multiple = True
                # left,    right
                # r,t,m = 9,0,6
                right = [right] + self.list_expression(tokens)
                if not isinstance(left,list):
                    #left is not list , right is list
                    # a = 9,2,3,4,5
                    # convert it to array
                    right = ast.Array(right,line_num)
                
                else:
                    # both are list
                    # assert number of left items equals right
                    assert_expression(len(left) == len(right), 'assignment items count not equal to right',line_num)
        else:
            #right item is not list
            # assert left item also is not list
            assert_expression(not isinstance(left,list),'cant assign multiple value to single expression',line_num)
        if tokens.check_expected("QUE"):
            # a = 9 ? 6==9:8
            self.eat(tokens,'QUE')
            test = self.parse_expression(tokens)
            if not test:
                raise ParserError('Syntax Error: expected  comparism operator',tokens.current)
            self.eat(tokens,"COLON")
            right2 = self.parse_expression(tokens)
            # check if right-2 is also multiple value eg, va1,val2
            if tokens.current.name == 'COMMA':
                right2 = [right2] + self.list_expression(tokens)
                if not isinstance(left,list):
                    right2 = ast.Array(right2,line_num)
                else:
                    assert_expression(len(left) == len(right2), 'assignment items count not equal to right',line_num)
            else:
                assert_expression(not isinstance(left,list),'assignment errors',line_num)
            if not right2:
                raise ParserError('Syntax Error: expect a value',tokens.current)
        self.eat(tokens,'NEWLINE')
        return ast.Assignment(left, right,test,right2,line_num)

    def array_expression(self,tokens):

        line_num = tokens.current.line
        self.eat(tokens,'LBRACK')
        items = self.list_expression(tokens)
        self.eat(tokens,'RBRACK')
        return ast.Array(items,line_num)

    def attr_expression(self,tokens,obj):

        line_num = obj.line
        self.eat(tokens,'DOT')
        attr = tokens.current
        if attr.name == 'FOREACH':
            return self.parse_foreach_statement(tokens,obj)
        attr =attr.value
        self.eat(tokens,"NAME")
        if not tokens.current.name == "LPAREN":
            # no arguments
            return ast.Objcall(obj,attr,[],line_num)
        self.eat(tokens,"LPAREN")
        args = self.list_expression(tokens)
        self.eat(tokens,"RPAREN")
        return ast.Objcall(obj,attr,args,line_num)

    def call_expression(self,tokens,left):

        keyword ={}
        line_num = left.line
        func_name = left.value
        if not isinstance(left,ast.Identifier):
            raise ParserError("SyntaxError: ",tokens.current)
        self.eat(tokens,'LPAREN')
        arguments = self.list_expression(tokens)
        if  tokens.current.name == "ASSIGN":
            keyword =  self.function_keys(tokens,func_name)
            if keyword:
                # del last item, it is part of keywords
                del arguments[-1]
        self.eat(tokens,'RPAREN')
        return ast.Call(func_name, arguments,keyword,line_num)

    def identifier_expression(self,tokens):

        token = self.eat(tokens,'NAME')
        return ast.Identifier(token.value,token.line)

    def compare_expression(self,tokens,left):
        # ==,>,< , <=, >=, + ,-,
        op = 'OPERATOR'
        pre = self.get_precedence(tokens.current)
        token = self.eat(tokens,op)
        right = self.parse_expression(tokens,pre)
        if right is None:
            raise ParserError('Expected right expression', tokens.current)
        current_pre = self.get_precedence(tokens.current)
        if current_pre != -1 and current_pre > pre:
            left = ast.BinaryOperator(token.value, left, right,token.line)
            parser = self.get_infix_parser(tokens.current.name)
            if parser:
                return parser(tokens,left)
        return ast.BinaryOperator(token.value, left, right,token.line)

    def logical_expression(self,tokens,left):
        op = tokens.current # and,or,in
        pre = self.get_precedence(op)
        token = self.eat(tokens,op.name)
        right = self.parse_expression(tokens,pre)
        if right is None:
            raise ParserError('Expected right expression', tokens.current)
        current_pre = self.get_precedence(tokens.current)
        if current_pre != -1 and current_pre > pre:
            left =  ast.LogicalOperator(left,right,op.name.lower(),op.line)
            parser = self.get_infix_parser(tokens.current.name)
            if parser:
                return parser(tokens,left)
        return ast.LogicalOperator(left,right,op.name.lower(),op.line)

    def not_expression(self,tokens):
        not_ = self.eat(tokens,"NOT")
        exp = self.parse_expression(tokens)
        if not exp:
            raise ParserError("SyntaxError: ",not_)
        return ast.NotOperator(exp,not_.line)

    def subscript_expression(self,tokens,left):
        '''p[1] = 98'''
        self.eat(tokens,'LBRACK')
        key = self.parse_expression(tokens)
        if key is None:
            raise ParserError('Subscript operator key is required', tokens.current)
        self.eat(tokens,'RBRACK')
        return ast.SubscriptOperator(left, key,left.line)


    def function_keys(self,tokens,fun):
        # function call keyeywords
        key =tokens.prev.value
        kwargs = {}
        tokens.advance()
        value = self.parse_expression(tokens)
        kwargs[key] = value
        if  tokens.current.name == "RPAREN":
            return kwargs
        self.eat(tokens,'COMMA')
        while not tokens.is_end() :
            key = self.eat(tokens,'NAME')
            if tokens.current.name in ('COMMA',"RPAREN"):
                raise ParserError(f" {fun}() got positional '{key.value}' arguements after keywords arguements",tokens.current)
            if  tokens.current.name == "ASSIGN":
                tokens.advance()
                value = self.parse_expression(tokens)
                if value:
                    k,v = key.value,value
                    if k in kwargs:
                        raise ParserError(f"multiple keywords for '{k}' of function {fun}()",tokens.current)
                    kwargs[k] = v
                    if tokens.current.name == 'RPAREN':
                        break
                    self.eat(tokens,'COMMA')
                    continue
                raise ParserError(f"could'nt parse value for keyword '{key.value}' of function {fun}()",tokens.current)
            raise ParserError(f" invalid syntax in function call",tokens.current)
        return kwargs

    def list_expression(self,tokens):
        # (f,g,h,h,j)
        items = []
        if tokens.current.name == 'COMMA':
                self.eat(tokens,'COMMA')
        while not tokens.is_end():
            exp = self.parse_expression(tokens)
            if exp is not None:
                items.append(exp)
            else:
                break
            if tokens.current.name == 'COMMA':
                self.eat(tokens,'COMMA')
            else:
                break
        return items

    def dict_expression(self,tokens):

        line_num = tokens.current.line
        self.eat(tokens,'LCBRACK')
        items = self.parse_dict_items(tokens)
        self.eat(tokens,'RCBRACK')
        return ast.Dictionary(items,line_num)

    def parse_dict_items(self,tokens):

        items = []
        while not tokens.is_end():
            # aloows using string or identifier as dict key like javascript
            # {name:'myname'},{'name':'myname'}
            if tokens.current.name == "NAME":
                key = self.eat(tokens,'NAME')
            elif tokens.current.name == 'STRING':
                key = self.eat(tokens,'STRING')
            else:
                break
            if key is not None:
                self.eat(tokens,'COLON')
                value = self.parse_expression(tokens)
                if value is None:
                    raise ParserError('Dictionary value expected', tokens.current)
                items.append((key, value))
            else:
                break
            if tokens.current.name == 'COMMA':
                self.eat(tokens,'COMMA')
            else:
                break
        return items


class Statement(BaseParser):

    def block_parser(self,tokens):
        self.eat(tokens,'NEWLINE', 'INDENT')
        statements = self.parse(tokens)
        self.eat(tokens,'DEDENT')
        return statements


    def parse_function_params(self,tokens,function):
        # function/class declarations args and kwargs
        params = []
        keys = {}
        if tokens.current.name == 'NAME':
            while not tokens.is_end() and tokens.current.name != "RPAREN":
                keyword = False
                id_token = self.eat(tokens,'NAME')
                if tokens.current.name == 'COMMA':
                    self.eat(tokens,'COMMA')
                elif tokens.current.name == "ASSIGN":
                    tokens.advance()
                    keyword  = True
                    exp = self.parse_expression(tokens)
                    if exp:
                        key,val = id_token.value,exp
                        if key in keys:
                            raise ParserError(f'{function}() got multiple keyword arguemnts for {key}',tokens.current)
                        keys[key] = val
                        if tokens.current.name == 'RPAREN':
                            break
                        self.eat(tokens,'COMMA')
                        continue
                    raise ParserError("invalid syntax in function arguements",tokens.current)
                else:
                    if tokens.current.name == "RPAREN":
                        if keys:
                            raise ParserError("positional argument after keyword argument",tokens.current)
                if not keyword:
                    if id_token.value in params:
                       raise ParserError(f'{function}() got multiple  arguements for {id_token.value}',tokens.current)
                    params.append(id_token.value)
                    # params.append(tokens.current.value) if not keyword else None
        else:
            self.eat(tokens,'NAME')
        return params,keys

    def parse_function_statement(self,tokens):

        self.eat(tokens,'FUNCTION')
        id_token = fun_name = self.eat(tokens,'NAME')
        if tokens.peek.name == "RPAREN":
            # no parameters
            self.eat(tokens,'LPAREN', "RPAREN",'COLON')
            arguments,kwargs = [],{}
        else:
            fun_name = id_token
            self.eat(tokens,'LPAREN')
            arguments,kwargs = self.parse_function_params(tokens,fun_name.value)
            self.eat(tokens,'RPAREN', 'COLON')
        with self as parser:
            parser.scope.append('function')
            block = self.block_parser(tokens)
        if block is None:
            raise ParserError('Expected function body', tokens.current)
        return ast.Function(id_token.value, arguments,kwargs, block,id_token.line)

    def parse_return_statement(self,tokens):
        if 'function' not in self.scope:
            raise ParserError('return outside function',tokens.current) 
        line_num = tokens.current.line
        self.eat(tokens,'RETURN')
        value = self.parse_expression(tokens)
        self.eat(tokens,'NEWLINE')
        return ast.Return(value,line_num)

    def parse_if_statement(self,tokens):

        self.eat(tokens,'IF')
        line_num = tokens.current.line
        test = self.parse_expression(tokens)
        if test is None:
            raise ParserError('Expected `if` condition', tokens.current)
        self.eat(tokens,'COLON')
        if_block = self.block_parser(tokens)
        if if_block is None:
            raise ParserError('Expected if body', tokens.current)
        elif_conditions = self.parse_elif_conditions(tokens)
        else_block = self.parse_else(tokens)
        return ast.Condition(test, if_block, elif_conditions, else_block,line_num)

    def parse_else(self,tokens):
        else_block = None
        if not tokens.is_end() and tokens.current.name == 'ELSE':
            self.eat(tokens,'ELSE', 'COLON')
            else_block = self.block_parser(tokens)
            if else_block is None:
                raise ParserError('Expected `else` body', tokens.current)
        return else_block

    def parse_elif_conditions(self,tokens):
        conditions = []
        while not tokens.is_end() and tokens.current.name == 'ELIF':
            line_num = tokens.current.line
            self.eat(tokens,'ELIF')
            test = self.parse_expression(tokens)
            if test is None:
                raise ParserError('Expected `elif` condition', tokens.current)
            self.eat(tokens,'COLON')
            block = self.block_parser(tokens)
            if block is None:
                raise ParserError('Expected `elif` body', tokens.current)
            conditions.append(ast.ConditionElif(test, block,line_num))
        return conditions

    def parse_else_condition(self,tokens):
        else_block = None
        if not tokens.is_end() and tokens.current.name == 'ELSE':
            self.eat(tokens,'ELSE', 'COLON')
            else_block = self.block_parser(tokens)
            if else_block is None:
                raise ParserError('Expected `else` body', tokens.current)
        return else_block

    def parse_try_statement(self,tokens):

        line_num = tokens.current.line
        self.eat(tokens,"TRY",'COLON')
        block = self.block_parser(tokens)
        if not block:
            raise ParserError(f'{t} try statement is required',tokens.current)
        self.eat(tokens,'CATCH')
        val = None
        var = tokens.check_expected ("NAME")
        if var:
            self.eat(tokens,'NAME')
            val = var.value    
        self.eat(tokens,'COLON')
        block_catch = self.block_parser(tokens)
        if not block_catch:
            raise ParserError(f'catch statement is required',tokens.current)
        return ast.Try(block,block_catch,val,line_num)

    def parse_for_statement(self,tokens):
        
        line_num = tokens.current.line
        self.eat(tokens,'FOR')
        var = self.eat(tokens,'NAME')
        self.eat(tokens,'IN')
        collection = self.parse_expression(tokens)
        self.eat(tokens,'COLON')
        with self as parser:
            parser.scope.append('loop')
            block = self.block_parser(tokens)
        if block is None:
            raise ParserError('Expected loop body', tokens.current)
        return ast.ForLoop(var.value, collection, block,line_num)

    def parse_while_statement(self,tokens):
        line_num = tokens.current.line
        self.eat(tokens,'WHILE')
        test = self.parse_expression(tokens)
        if test is None:
            raise ParserError('While condition expected', tokens.current)
        self.eat(tokens,'COLON')
        with self as parser:
            parser.scope.append('loop')
            block = self.block_parser(tokens)
        if block is None:
            raise ParserError('Expected loop body', tokens.current)
        return ast.WhileLoop(test, block,line_num)

    def parse_break_statement(self,tokens):
        if 'loop' not in self.scope:
            raise ParserError('break outside loop',tokens.current)
        line_num = tokens.current.line
        self.eat(tokens,"BREAK")
        break_test = None
        if tokens.check_expected("QUE"):
            self.eat(tokens,"QUE")
            break_test = self.parse_expression(tokens)
        self.eat(tokens,"NEWLINE")
        return ast.Break(break_test,line_num)

    def parse_continue_statement(self,tokens):
        if 'loop' not in self.scope:
            raise ParserError("continue outside loop",tokens.current.line)
        line_num = tokens.current.line
        self.eat(tokens,"CONTINUE")
        continue_test = None
        if tokens.check_expected("QUE"):
            self.eat(tokens,"QUE")
            continue_test = self.parse_expression(tokens)
        self.eat(tokens,"NEWLINE")
        return ast.Continue(continue_test,line_num)


    def parse_when(self,tokens):
        patterns = []
        while not tokens.is_end() and tokens.current.name == 'WHEN':
            line_num = tokens.current.line
            self.eat(tokens,'WHEN')
            pattern = self.parse_expression(tokens)
            if pattern is None:
                raise ParserError('Pattern expression expected', tokens.current)
            self.eat(tokens,'COLON')
            block = self.block_parser(tokens)
            patt =  ast.MatchPattern(pattern, block,line_num)
            patterns.append(patt)
        return patterns

    def parse_match_statement(self,tokens):

        line_num = tokens.current.line
        self.eat(tokens,'MATCH')
        test = self.parse_expression(tokens)
        self.eat(tokens,'COLON', 'NEWLINE', 'INDENT')
        patterns = self.parse_when(tokens)
        if not patterns:
            raise ParserError('One or more `when` pattern excepted', tokens.current)
        else_block = self.parse_else(tokens)
        self.eat(tokens,'DEDENT')
        return ast.Match(test, patterns, else_block,line_num)

    def parse_foreach_statement(self,tokens,obj):
        #obj.foreach => item:
        line_num = tokens.current.line
        self.eat(tokens,"FOREACH","FOREACHOP")
        name = self.eat(tokens,"NAME").value
        self.eat(tokens,'COLON')
        with self as parser:
            parser.scope.append('loop')
            body = self.block_parser(tokens)
        return ast.ForEach(obj,name,body,line_num)

    def parse_use_statement(self,tokens):
        line = self.eat(tokens,"USE").line
        alias = None
        module = self.eat(tokens,"NAME").value
        if tokens.check_expected("AS"):
            self.eat(tokens,"AS")
            alias = self.eat(tokens,"NAME").value
        self.eat(tokens,'NEWLINE')
        return ast.Use(module,alias,line)

    def parse_include_statement(self,tokens):
        line_num = self.eat(tokens,'INCLUDE').line
        func = self.eat(tokens,'NAME').value
        self.eat(tokens,'IN')
        file =  self.eat(tokens,'STRING').value
        self.eat(tokens,"NEWLINE")
        return ast.Include(func,file,line_num)

    def parse_class_statement(self,tokens):
        self.eat(tokens,'CLASS')
        args,kwargs = [], {}
        cls_name =self.eat(tokens,"NAME")
        if tokens.current.name == "COLON":
            # class nam:
            self.eat(tokens,"COLON")
        elif tokens.peek.name == "RPAREN":
            # current = '(' peek,')'
            # class n()
            self.eat(tokens,"LPAREN","RPAREN","COLON")
        else:
            self.eat(tokens,'LPAREN')
            args, kwargs = self.parse_function_params(tokens,cls_name.value)
            self.eat(tokens,"RPAREN","COLON")
        body = self.block_parser(tokens)
        # self.eat(tokens,"DEDENT")
        return ast.Class_(cls_name.value,args,kwargs,body,cls_name.line,{})





class Parser(Statement,Expression):

    def parse_all(self,tokens):
        programs = self.parse(tokens)
        return programs

    def __enter__(self):
        return self

    def __exit__(self,*args):
        self.pop()
    def pop(self):
        del self.scope[-1]

    def eat(self,tokens,*names):
        for name in names:
            token = tokens.consume_expected(name)
        return token


class Programs:

    def __init__(self,programs):
        self.programs = programs

    def get_program(self,name):
        return [f for f in self.programs if f._name == name]

    @property
    def count(self):
        return len(self.programs)

    def __getattr__(self,name):
        name = name.rstrip('_') # work around python keywords
        prog = self.get_program(name)
        return []  if not prog else prog

    

