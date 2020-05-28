from abbey.errors import AbbeySyntaxError


def assert_expression(exp,msg,line=None):
    try:
        assert exp,msg
    except AssertionError:
        raise AbbeySyntaxError(msg,line,5)


def report_syntax_error(lexer, error):
    line = error.line
    column = error.column
    print(line,column,'======')
    source_line = lexer.source_lines[line - 1]
    print('Syntax error: {} at line {}'.format(error.message, line, column))
    print(' '*3,'{}\n{}^'.format(source_line, ' ' * (column - 1)))

def report_error(lexer,error):
    line = error.line
    message = error.message
    print(' '*3,lexer.source_lines[line-1])
    print(error.message)



class Environment(object):

    def __init__(self, parent=None, args=None):
        self._parent = parent
        self._values = {}
        if args is not None:
            self._from_dict(args)

    def _from_dict(self, args):
        for key, value in args.items():
            self.set(key, value)

    def set(self, key, val):
        self._values[key] = val

    def get(self, key:int):
        val = self._values.get(key, None)
        if val is None and self._parent is not None:
            return self._parent.get(key)
        else:
            return val

    def asdict(self):
        return self._values

    def __repr__(self):
        return 'Environment({})'.format(str(self._values))


class Errormessage:

    error = {
     "NAME" : 'expected an identifier',
     "COLON" : "expected a colon",
     "LPAREN":'expected a bracket "(" ',
     "RPAREN":'expected a bracket ")"',
     "IN":'expected "in"',
     "CATCH": 'expected a catch body',
     "COMMA" :'expected a comma "," ',
     "INDENT": "expected an indented block"

    }

    def get_error(self,name):

        msg = self.error.get(name)
        return msg