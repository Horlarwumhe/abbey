"""
Errors
------

Exceptions and exception helpers.
"""
### exception during parsing

class AbbeyBaseError(Exception):
    ''' base error for all abbey errors
    '''

# errors in lexing and parsing phases
class AbbeySyntaxError(AbbeyBaseError):

    def __init__(self, message, line, column):
        super().__init__(message)
        self.message = message
        self.line = line
        self.column = column

class LexerError(AbbeySyntaxError):
    pass

class ParserError(AbbeySyntaxError):

    def __init__(self, message, token):
        super().__init__(message, token.line, token.column)


## exceptions during excecution
class AbbeyError(AbbeyBaseError):

    def __init__(self, message, line=None, column=None):
        self.message = message
        self.line = line
        self.column = column
        self.type = self.__class__.__name__

class NameError_ (AbbeyError):
    pass

class AttributeError_(AbbeyError):
    pass
        
class TypeError_(AbbeyError):
    pass


class IndexError_(AbbeyError):
    pass


class AbbeyModuleError(AbbeyBaseError):
    """ exception when importing a module
    """
    def __init__(self,message,line,source_lines,column=1,file=''):
        self.message = message
        self.line = line
        self.column = column
        self.source_lines = source_lines
        self.file = file