from abbey.utils import Errormessage
from abbey.errors import LexerError
class Tokens(object):

    def __init__(self, tokens):
        self._tokens = self.tokens = tokens
        self._pos = 0

    def consume_expected(self, *args,msg=None):
        token = None
        for expected_name in args:
            token = self.now
            self.advance()
            if token.name != expected_name:
                err = Errormessage().get_error(expected_name)
                if not err:
                    raise LexerError('Expected {}, got {}'.format(expected_name, token.name), token.line, token.column)
                raise LexerError('{}'.format(err), token.line, token.column)

        return token

    def check_expected (self,name):
        current = self.current
        if current.name == name:
            # not all tokens has value
            return current
        return False
    @property
    def next(self):
        try:
            self._pos += 1
            return self._tokens[self._pos]
        except:
            return None

    @property
    def peek(self):
        try:
            return self._tokens[self._pos+1]
        except:
            return None
    
    @property
    def now(self):
        try:
            return self._tokens[self._pos]
        except IndexError:
            last_token = self._tokens[-1]
            raise LexerError('Unexpected end of input', last_token.line, last_token.column)
    def advance(self):
        try:
            self._pos += 1
            return self._tokens[self._pos]
        except:
            return None
    
    @property
    def current(self):
        try:
            return self._tokens[self._pos]
        except IndexError:
            last_token = self._tokens[-1]
            raise LexerError('Unexpected end of input', last_token.line, last_token.column)
    @property
    def prev(self):
        return self._tokens[self._pos-1]
    
    def expect_end(self):
        if not self.is_end():
            token = self.current
            raise LexerError('End expected', token.line, token.column)

    @property
    def seen_all(self):
        return self._pos == len(self._tokens)

    @property
    def line(self):
        return self.current.line

    def is_end(self):
        return self._pos == len(self._tokens)