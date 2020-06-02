"""
Errors
------

Exceptions and exception helpers.
"""
### exception during parsing

class AbbeyBaseError(Exception):
    ''' base errorfor all abbey errors
    '''
class AbbeySyntaxError(AbbeyBaseError):

    def __init__(self, message, line, column):
        super(AbbeySyntaxError, self).__init__(message)
        self.message = message
        self.line = line
        self.column = column

class LexerError(AbbeySyntaxError):
    def __init__(self,msg,line=None,column=None):
        self.message = msg
        self.line = line
        self.column = column

class ParserError(AbbeySyntaxError):

    def __init__(self, message, token):
        super(ParserError, self).__init__(message, token.line, token.column)

## exceptions during excecution
class AbbeyError(AbbeyBaseError):

    def __init__(self, message, line=None, column=None):
        super(AbbeyError, self).__init__(message)
        self.message = message
        self.line = line
        self.column = column
        self.type = self.__class__.__name__

class NameError_ (AbbeyError):
    def __init__(self, message,line=None):
        self.line = line
        super(NameError_, self).__init__(message,line,None)

class AttributeError_(AbbeyError):
    """docstring for AttributeError"""
    def __init__(self, message,line=None):
        self.line = line
        super(AttributeError_, self).__init__(message,line,None)
        
class TypeError_(AbbeyError):
    """docstring for AttributeError"""
    def __init__(self, message,line):
        self.line = line
        super().__init__(message,line,None)


class IndexError_(AbbeyError):
     def __init__(self, message,line):
        self.line = line
        super().__init__(message,line,None)


class AbbeyModuleError(AbbeySyntaxError):
    """ exception when importing a module
    """
    def __init__(self,message,line,source_lines,column=1,file=''):
        self.message = message
        self.line = line
        self.column = column
        self.source_lines = source_lines
        self.file = file