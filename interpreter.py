import importlib
import os
import re

from abbey import ast
from abbey._types import List, Dict,String, Int
from abbey.utils import Environment,assert_expression
from abbey._builtins import Builtins, Str, load_builtins
from abbey.errors import * # import all exceptions
from abbey import operators
from abbey.importer import load_module

str_format = re.compile(r'#\{\s*(\w+)\s*\}')

nodes = {
    ast.Number: 'visit_number',
    ast.String: "visit_string",
    ast.Array:"visit_array",
    ast.Dictionary: "visit_dict",
    ast.Identifier: "visit_identifier",
    ast.BinaryOperator: "visit_binary_operator",
    ast.NotOperator: "visit_not",
    ast.SubscriptOperator: "visit_getitem",
    ast.Assignment: "visit_assignment",
    ast.Condition: "visit_condition",
    ast.Match: "visit_match",
    ast.WhileLoop: "visit_while_loop",
    ast.ForLoop: "visit_for_loop",
    ast.Function: "visit_function_declaration",
    ast.Call: "visit_call",
    ast.Return: "visit_return",
    ast.Objcall:"visit_objcall",
    ast.Try: "visit_try",
    ast.ForEach:'visit_foreach',
    ast.Use: "visit_use",
    ast.Break : "visit_break",
    ast.Continue :'visit_continue',
    ast.LogicalOperator:'visit_logical',
    ast.Include:'visit_include',
    ast.Class_:'visit_class'
}

class Operators:

    simple_operations = {
            '+': operators.add,
            '-': operators.sub,
            '*': operators.mul,
            '/': operators.div,
            '%': operators.mod,
            '..': range,
            '...': lambda start, end: range(start, end + 1),
        }
    comaprism = {
             '>': operators.gt,
            '>=': operators.ge,
            '<': operators.lt,
            '<=': operators.le,
            '==': operators.eq,
            '!=': operators.ne,
            "**":operators.sqrt,
            '<>':lambda x,y: x != y
        }
    aug_operator = {
    '-=':operators.sub,
    '+=':operators.add,
    '/=':operators.div,
    '*=':operators.mul
    }
    logical = {
        'and': lambda x,y:x and y,
        'or': lambda x, y: x or y,
        'in':operators.contains,
    }

class Break(Exception):
    pass


class Continue(Exception):
    pass


class Return(Exception):
    def __init__(self, value):
        self.value = value

class Interpreter:

    def __init__(self,programs,path=None):
        self.path = path # current path of the file
        self.programs = programs
        self.nodes = {}
        self.env = None

    def create_env(self,default_env=None):
        env = Environment()
        if default_env is not None:
            env = default_env
        self.env =env
        load_builtins(env)
    
    def visit_class(self,node,env):
        env.set(node.name,node)

    def get_node_function(self,node):
        func_str = nodes.get(type(node))
        assert func_str is not None , "unknow node type {}".format(type(node))
        func = getattr(self,func_str,None)
        assert func is not None , f"{self.__class__.__name__} has no function for {type(node)}"
        return func
    def interpret(self):
        ret = None
        for program in self.programs:
            func = self.get_node_function(program)
            ret = func(program,self.env)
        return ret

    def visit_string(self,node,env):
        """string node"""
        def strsub(match):
            value = match.group(1)
            return str(env.get(value))
        value = str_format.sub(strsub,node.value)
        return String(value)

    def visit_number(self,node,env):
        """number node"""
        return Int(node.value)

    def visit_statements(self,statement,env):
        ''' for nodes that has body, iterate of the body and visit all nodes
        eg. if statement, func statement'''
        for node in statement:
            func = self.get_node_function(node)
            ret = func(node,env)
        return ret
    def visit_expression(self,node,env):
        func = self.get_node_function(node)
        return func(node,env)

    def multi_assignment(self,node,env,side=None):
        '''item1,item2,item3 = val1,val2,val3 ? condition : val4,val5,val6
        '''
        for item,value in zip(node.left,node.right):
            if isinstance(item,(ast.SubscriptOperator,ast.Objcall)):
                # this is not supported yet
                # item, d[key] = val1,val2
                # item, class.method = val1,val2
                raise TypeError_('assignment type not supported',node.line)

        # v = right ? cond : right2
        # assign to right , if cond return True,else assignt to right2
        if side == 'right':
            for item,value in zip(node.left,node.right):
                assign = env.set(item.value, self.visit_expression(value, env))
            return assign
        elif side == 'right2':
            for item,value in zip(node.left,node.right2):
                assign = env.set(item.value, self.visit_expression(value, env))
            return assign

    def obj_assignment(self,node,env,right=True):
        # node, assignment node
        # obj.attr = new
        obj = self.visit_expression(node.left.obj,env)
        assert_expression(isinstance(obj,ast.Class_), 'cant set attribute of %s'%obj,node.line)
        attr = obj.env.get(node.left.attr)
        if isinstance(attr,ast.Function):
            # obj.meth() = 8 or obj.meth = 6
            # if meth is function
            # raise an error
            raise TypeError_('cant assign to function call',obj.line)
        if right:
            value = node.right
        else:
            value = node.right2
        return obj.env.set(node.left.attr,self.visit_expression(value,env))


    def visit_assignment(self,node,env):
        if not hasattr(node,'test'):
            setattr(node,'test',False)
        left = node.left
        if isinstance(left,ast.SubscriptOperator):
            # c[key] =value
            return self.visit_setitem(node,env)
        elif node.test:
            # value = name ? cond : name 2
            test = self.visit_expression(node.test,env)
            if isinstance(node.left,list):
                # item1,item2 = val1,val2 ? cond : val3,val4
                side = {True:'right',False:'right2'}
                return self.multi_assignment(node,env,side=side[bool(test)])
            elif isinstance(node.left,ast.Objcall):
                #class.method = val ? cond : val2 
                return self.obj_assignment(node,env,right=bool(test))
            else:
                # value = name ? cond : name 2
                if test:
                    return env.set(node.left.value,self.visit_expression(node.right, env))
                else:
                    return env.set(node.left.value,self.visit_expression(node.right2, env))
        elif isinstance(node.left,list):
            #item1,item2 = val1, val2
            for item,value in zip(node.left,node.right):
                if isinstance(item,(ast.SubscriptOperator,ast.Objcall)):
                    # b,dict[key] = val1, val2 
                    # not supported yet
                    raise TypeError_('assignment type not supported',node.line)
                assign = env.set(item.value, self.visit_expression(value, env))
            return assign
        elif isinstance(node.left,ast.Objcall):
            # class.attr = value
            return self.obj_assignment(node,env,right=True)
            
        else:
            # item = value
            return env.set(node.left.value,self.visit_expression(node.right, env))

    def visit_getitem(self,node,env):
        """list or string or dict getitem method dict[key], list[7:9]"""
        data  = self.visit_expression(node.left,env)
        if isinstance(node.key,slice):
            # list[2:7]
            start = node.key.start
            stop = node.key.stop
            if start:
                start = self.visit_expression(start,env)
            if stop:
                stop = self.visit_expression(stop,env)
            key = slice(start,stop)
        else:
            key = self.visit_expression(node.key,env)
        try:
            return data[key]
        except IndexError as e:
            raise IndexError_(e,node.line)
        except KeyError:
            raise IndexError_("KeyError, no such key '%s'"%key,node.line)
        except TypeError as e:
            raise TypeError_(e,node.line)


    def visit_setitem(self,node,env):
        """ # dict[key] = value
            list[index] = value
            list[start:stop] = values
        """
        subscript = node.left
        data = self.visit_expression(subscript.left,env)
        if isinstance(subscript.key,slice):
            start = subscript.key.start
            stop = subscript.key.stop
            if start:
                start = self.visit_expression(start,env)
            if stop:
                stop = self.visit_expression(stop,env)
            key = slice(start,stop)
        else:
            key = self.visit_expression(subscript.key,env)
        value  = self.visit_expression(node.right,env)
        if node.test:
            test_pass = self.visit_expression(node.test,env)
            if not test_pass:
                value = self.visit_expression(node.right2,env)
        try:
            data[key] = value
        except IndexError:
            raise IndexError_('assignment index out of range')
        except TypeError as e:
            raise TypeError_(e,node.line)

    def visit_objcall (self,node,env):
        '''obj.atr
        obj.attr(arg1,arg2)
        'hello'.count('h')
        '''
        obj = self.visit_expression(node.obj,env)
        attr = node.attr
        args = [self.visit_expression(n,env) for n in node.arguements]
        if isinstance(obj,ast.Class_):
            cls_attr = obj.env.get(attr)
            if cls_attr is None:
                raise AttributeError_('class %s object has no attribute "%s" '%(obj.name,attr),node.line)
            new_env = Environment(env)
            new_env.set('this',obj)
            return self.visit_class_obj(cls_attr,new_env,args,kls=obj,node=node)
        func = getattr(obj,attr,None)
        if not func:
            raise AttributeError_(f'{obj.__class__.__name__} object has no atrribute "{attr}',node.line)
        try:
            return func(*args) if callable(func) else func
        except TypeError as e:
            raise TypeError_(e,node.line)

    def visit_try(self,node,env):
        '''try statement'''

        errors = []
        try:
            body = self.visit_statements(node.body,env)
        except Exception as e:
            errors.append(str(e))
            try:
                var = node.catch_var
                if var:
                    env.set(var,e)
                body = self.visit_statements(node.catch_body,env)
            except Exception as x:
                # raise exceptions that occur in try block and catch block
                errors.append(str(x))
                f = '\n\n'+errors[0] +'\n'*2
                line = node.line
                s = 'during handling above exception another exception occurs'+'\n'*2+ errors[1]
                if hasattr(e,'line'):
                    line = e.line
                raise AbbeyError(f+s,line)
        return body

    def visit_identifier(self,node, env):
        name = node.value
        val = env.get(name)
        if val is None:
            raise NameError_('NameError: Name "{}" is not defined'.format(name),node.line)
        return val

    def visit_match(self,node, env):
        '''match statement'''
        test = self.visit_expression(node.test, env)
        for pattern in node.patterns:
            if self.visit_expression(pattern.pattern, env) == test:
                return self.visit_statements(pattern.body, env)
        if node.else_body is not None:
            return self.visit_statements(node.else_body, env)

    def visit_while_loop(self,node, env):
        '''while loop'''
        while self.visit_expression(node.test, env):
            try:
                self.visit_statements(node.body, env)
            except Break:
                break
            except Continue:
                continue

    def visit_for_loop(self,node, env):
        '''for loop'''
        var_name = node.var_name
        collection = self.visit_expression(node.collection, env)
        for val in collection:
            env.set(var_name, val)
            try:
                self.visit_statements(node.body, env)
            except Break:
                break
            except Continue:
                pass
    def visit_break(self,node,env,*args):
        '''break, 
           break? 1==1; if 1==1:break
        '''
        if node.test:
            test = self.visit_expression(node.test,env)
            if test: # test return True
                raise Break()
            return
        raise Break()

    def visit_continue(self,node,env,*args):
        '''same as break '''
        if node.test:
            test = self.visit_expression(node.test,env)
            if test:
                raise Continue()
            return
        raise Continue()

    def visit_function_declaration(self,node, env):
        ''' function declaration'''
        return env.set(node.name, node)


    def visit_class_obj(self,func,func_env,args,kls=None,node=None):
        ''' visit function call of a class or class attribute
         class() ,class.method()
        '''
        if not isinstance(func,ast.Function):
            return func
        if len(args) != len(func.arguements):
            raise TypeError_ ('method "%s" of  class "%s" takes %s arguments %s were given'%(
                                func.name,func_env.get('this').name,len(func.arguements),len(args)),
                                node.line
                            )
        args = dict(zip(func.arguements, args))
        func_env.from_dict(args)
        try:
            return self.visit_statements(func.body,func_env)
        except Return as ret:
            return ret.value
        except AbbeyBaseError as e:
            line = e.line
            if hasattr(kls,'import_'):
                    #imported kls,indicate the module name and line
                    raise TypeError_(" %s , in file '%s' line %s "%(e.message,kls.file,line),line)
            raise TypeError_(e,line)


        else:
            return 'None'
    def visit_call(self,node, env):
        '''visit call , eg ,factorial(10)'''
        function = env.get(node.name)
        if function is None:
            raise NameError_('NameError: Name "{}" is not defined'.format(node.name),node.line)

        if isinstance (function,Builtins):
            # builtin functions
            args = [self.visit_expression(arg, env) for arg in node.arguements]
            kwargs = {k:self.visit_expression(v, env) for k, v in node.keywords.items()}
            function.check_args(node) # check number of args provide, match required
            try:
                return function.callback(*args,**kwargs)
            except Exception as e:
                raise TypeError_(e,node.line)

        if not isinstance(function,(ast.Class_,ast.Function)):
            # 7(), s = 'hello', s()
            # raise error
            raise TypeError_("%s is not callbale"%function,node.line)

        fun_kwargs = dict(zip(function.keywords.keys(), [self.visit_expression(value,env) for value in function.keywords.values()]))
        # function keywords , func name(n,t=4,m=5)
        call_kwargs = dict(zip(node.keywords.keys(), [self.visit_expression(value,env) for value in node.keywords.values()]))
        # call keywords name('hd',m=98)
        expect = len(function.arguements)
        given = len(node.arguements)
        m = [*node.arguements]
        if expect != given:
            raise TypeError_('TypeError: {}() takes {} positional argument but {} were given '.format(function.name,expect, given),node.line)
        args = dict(zip(function.arguements, [self.visit_expression(value, env) for value in m]))
        if isinstance(function,ast.Class_):
            klass = function
            newenv = Environment(env,{'this':klass})
            newenv.from_dict(fun_kwargs,call_kwargs,args)
            klass.env = newenv
            self.visit_statements(klass.body,newenv)
            klass.env = newenv
            return klass 

        elif isinstance(function,ast.Function):
            function.check_args(node)
            call_env = Environment(env, args)
            # set kwargs in function to env
            call_env.from_dict(fun_kwargs,call_kwargs)
            #set kwargs in function call to env to overide kwargs in function def.
            try:
                self.visit_statements(function.body, call_env)
            except Return as ret:
                return ret.value
            except AbbeyBaseError as e:
                if hasattr(function,'import_'):
                    #imported function,indicate the module name and line
                    raise TypeError_(" %s , in file '%s' line %s "%(e.message,function.file,e.line),node.line)
                raise TypeError_(e,e.line)

            else:
                # no return in the function
                return "None"

    def visit_array(self,node, env):
        '''m =[]'''
        l = [self.visit_expression(item, env) for item in node.items]
        return List(l)


    def visit_dict(self,node, env):
        '''k ={}'''
        d = {key.value: self.visit_expression(value, env) for key, value in node.items}
        return Dict(d)



    def visit_return(self,node, env):
        ''' return from a function'''
        exp = self.visit_expression(node.value, env) if node.value is not None else None
        raise Return(exp)


    def visit_condition(self,node, env):
        ''' if condition'''
        if self.visit_expression(node.test, env):
            return self.visit_statements(node.if_body, env)

        for cond in node.elifs:
            if self.visit_expression(cond.test, env):
                return self.visit_statements(cond.body, env)

        if node.else_body is not None:
            return self.visit_statements(node.else_body, env)

    def visit_binary_operator(self,node, env):
        ''' operators 
           1 + 8, 4 * 7
           7 == 9, 8 <= 9
           h += 5
        '''
        left, right = self.visit_expression(node.left, env), self.visit_expression(node.right, env)
        if node.operator in Operators.simple_operations:
            return Operators.simple_operations[node.operator](left,right)
        elif node.operator in Operators.comaprism:
            return Operators.comaprism[node.operator](left,right)
        elif node.operator in Operators.aug_operator:
            # += -=
            right = Operators.aug_operator[node.operator](left,right)

            if isinstance(node.left,ast.Identifier):
                return env.set(node.left.value,right)
        else:
            raise Exception('Invalid operator {}'.format(node.operator))

    def visit_logical(self,node,env):
        '''in , and , or'''
        left = self.visit_expression(node.left,env)
        right = self.visit_expression(node.right,env)
        return Operators.logical[node.operator](left,right)

    def visit_not(self,node,env):
        '''not '''
        right = self.visit_expression(node.right,env)
        return not right

    def visit_foreach(self,node,env):
        '''seq.foreach=>var:'''
        obj = self.visit_expression(node.obj,env)
        if isinstance(obj,int):
            obj = str(obj)
        var_name = node.var_name
        for item in obj:
            env.set(var_name,item)
            try:
                ret = self.visit_statements(node.body,env)
            except Break:
                break
            except Continue:
                continue
        return 

    def visit_use(self,node,env):
        '''use, for importing module from python'''
        module = node.module
        alias = node.alias
        try:
           mod = importlib.import_module(module)
        except ImportError:
            raise TypeError_('couldn\'t find module, "%s" '%module,node.line)
        name = alias or module # name to use in the environment if alias is given use it else use module name
        return env.set(name,mod)


    def visit_include(self,node,env):
        '''importing local module,
        not stable yet may be remove later
        '''
        func_name = node.function
        file = node.file.rstrip('.ab')+'.ab'
        #check if it is already in env before importing it
        func = env.get(node.function)
        if func:
            setattr(func,'import_',True)
            setattr(func,'file',file)
            env.set(func_name,func)
            return
        if self.path is not None:
            path = os.path.join(self.path,file)
            try:
                buff = open(path)
                content = buff.read()
                buff.close()
            except FileNotFoundError:
                raise TypeError_("module not found %s"%path,node.line)
            try:
                import_env= load_module(content,self)
            except Exception as e:
                if isinstance(e,AbbeyBaseError):
                    column = 1
                    if hasattr(e,'column') and e.column is not None:
                        column = e.column
                    raise AbbeyModuleError("%s"%(e.message),e.line,content.splitlines(),column,file)
                # the exception must be instance of AbbeyBaseError
                # if it is not, something bad occurs, so raise RuntimeError
                raise RuntimeError(e)
            else:
                func = import_env.get(func_name)
                if func is None:
                    raise TypeError_('couldnt import "%s" from "%s" '%(func_name,path),node.line)
                setattr(func,'import_',True) #to indicate it is an imported function
                setattr(func,'file',path) # file where it is imported
                env.set(func_name,func)







    
