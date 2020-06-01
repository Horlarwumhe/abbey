from abbey.errors import TypeError_



class Node:
    fields = ()
    exclude = () # excluded fields in str representation

    def __init__(self,*fields_):
        if len(self.fields) != len(fields_):
            # RuntimeError , for internal use only
            raise RuntimeError('%s Node, takes %s args [%s] but %s  are give'%(self.__class__.__name__,
                       len(self.fields),','.join(self.fields),len(fields_), )
                )
        for field_name,field_value in zip(self.fields,fields_):
            setattr(self,field_name,field_value)

    def __str__(self):
        s = f"<{self.__class__.__name__} "
        for name in self.fields:
            if name in self.exclude:
                continue
            try:
                # handle d exception
                # dont use getattr(self,f,None)
                # some attribute return none value
                value = getattr(self,name)
            except AttributeError:
                continue
            if hasattr(value,'value'):
                value = value.value
            s += ' {} = "{}",'.format(name,value)
        s += ">"
        return s

    def __repr__(self):
        return str(self)

class Number(Node) :
    _name = 'num'
    fields = ('value','line')
        
class String(Node) :
    _name = 'str'
    fields = ('value','line')
        
class Identifier(Node) :
    _name = 'id'
    fields = ('value','line')

class Function(Node):
    _name = 'function'
    fields = ("name","arguements","keywords","body","line")
    exclude = ('body',)

    def check_args(self,call):
        self.parser_kwargs(call)

    def parser_kwargs(self,call):
        for k in call.keywords:
            if k not in self.keywords:
                raise TypeError_(f"TypeError_ ,{call.name}() got unexpected keyword arguments {k}",call.line)
      
class Assignment(Node) :
    _name = 'assign'
    fields = ('left','right','test','right2','line')

        
class BinaryOperator(Node) :
    fields = ('operator','left','right','line')
   
class NotOperator(Node) :
    fields = ('right','line')
        
class Call(Node) :
    _name = 'call'
    fields = ("name","arguements","keywords","line")
    
        
class Condition(Node) :
    _name = 'if'
    fields = ('test','if_body','elifs','else_body','line')

    def __str__(self):

        return "<{}, test = {}, ifbody = {},line = {} else_body={}".format(self.__class__.__name__,
                    self.test,len(self.if_body),self.line,bool(self.else_body))
                
        
class ConditionElif(Node) :
    _name = 'elif'
    fields = ('test','body','line')
    exclude = ('body',)
        
class Match(Node) :
    _name = 'match'
    fields = ('test','patterns','else_body','line')
    def __str__(self):
        return f"{self.__class__.__name__}, test = {self.test}, pattern = {len(self.patterns)}, line = {self.line}"
        
class MatchPattern(Node) :
    _name = 'case'
    fields = ('pattern','body','line')
    exclude = ('body',)
        
class WhileLoop(Node) :
    _name = 'while'
    fields = ('test','body','line')
    exclude = ('body',)
        
class ForLoop(Node) :
    _name = 'for'
    fields = ('var_name','collection','body','line')
    exclude = ('body',)

        
class Break(Node) :
    _name = 'break'
    fields = ('test','line',)
        
class Continue(Node) :
    _name = 'continue'
    fields = ('test','line',)
        
class Return(Node) :
    _name = 'return'
    fields = ('value','line')
        
class Array(Node) :
    _name = 'list'
    fields = ('items','line')
        
class Dictionary(Node) :
    _name = 'dict'
    fields = ('items','line')
        
class SubscriptOperator(Node) :
    _name = 'subcript'
    fields = ('left','key','line')
        
class Program(Node) :
    def __init__(self,body,line=None):
        self.body = body

    def __str__(self):
        return "<Programs statements=%s>"%len(self.body)

    def get_node(self,name):
        return [node for node in self.body if node.__class__.__name__.lower() == name]

        
class Objcall(Node):
    _name = 'objcall'
    fields = ('obj','attr','arguements','line')

        
class Try (Node):
    _name = 'try'
    fields = ('body','catch_body','catch_var','line')
    exclude = ('body','catch_body')


class ForEach(Node):
    _name = 'foreach'
    fields = ('obj','var_name','body','line')
    exclude =('body',)


class Use(Node):
    _name = 'use'
    fields = ('module','alias','line')

class Include(Node):
    _name = 'include'
    fields = ('function','file','line')

class LogicalOperator(Node):
    # in , and ,or 
    _name = 'logical'
    fields  = ('left','right','operator','line')

class Class_(Node):

    _name = 'class'
    fields = ('name','arguements','keywords',"body",'line','env')

    def load_env(self):
        for node in self.body:
            if isinstance(node,Assignment):
                self.env[node.left] = node
            elif isinstance(node,Function):
                self.env[node.name] = node

