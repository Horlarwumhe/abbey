import importlib
from collections import namedtuple


from abbey import ast
from abbey._types import List, Dict,String
from abbey.utils import Environment
from abbey._builtins import Builtins, Str, load_builtins
from abbey.errors import * # import all exceptions
from abbey import operators

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
    ast.LogicalOperator:'visit_logical'
}
BuiltinFunction = namedtuple('BuiltinFunction', ['params', 'body'])

class Operators:

    simple_operations = {
            '+': operators.add,
            '-': operators.sub,
            '*': operators.mul,
            '/': operators.truediv,
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
    logical = {
    'and': lambda x,y:x and y,
    'or': lambda x, y: x or y,
    'in':operators.contains,
    }
    # simple_operations.update(comaprism)
class Break(Exception):
    pass


class Continue(Exception):
    pass


class Return(Exception):
    def __init__(self, value):
        self.value = value

class Interpreter:

    def __init__(self,programs):
        self.programs = programs
        self.nodes = {}
        self.env = None

    def create_env(self,default_env=None):
        env = Environment()
        if default_env is not None:
            env = default_env
        self.env =env
        load_builtins(env)
        
    def get_node_function(self,node):
        func_str = nodes.get(type(node))
        assert func_str is not None , "unknow node type {}".format(type(node))
        func = getattr(self,func_str,None)
        assert func is not None , f"{self} has no function for {type(node)}"
        return func
    def interpret(self):
        ret = None
        for program in self.programs:
            func = self.get_node_function(program)
            ret = func(program,self.env)
        return ret

    def visit_string(self,node,env):
        return String(node.value)

    def visit_number(self,node,env):
        return node.value

    def visit_statements(self,statement,env):
        for node in statement:
            func = self.get_node_function(node)
            ret = func(node,env)
        return ret
    def visit_expression(self,node,env):
        func = self.get_node_function(node)
        return func(node,env)

    def multi_assignment(self,node,env,side=None):
        for item,value in zip(node.left,node.right):
            if isinstance(item,ast.SubscriptOperator):
                raise TypeError_('assignment type not supported',node.line)

        if side == 'right':
            for item,value in zip(node.left,node.right):
                assign = env.set(item.value, self.visit_expression(value, env))
            return assign
        elif side == 'right2':
            for item,value in zip(node.left,node.right2):
                assign = env.set(item.value, self.visit_expression(value, env))
            return assign


    def visit_assignment(self,node,env):
        # value = name
        # value[key] = name
        # value = name ? cond : name 2
        # value[key] = new ? cond : other
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
            else:
                # value = name ? cond : name 2
                if test:
                    return env.set(node.left.value,self.visit_expression(node.right, env))
                else:
                    return env.set(node.left.value,self.visit_expression(node.right2, env))
        elif isinstance(node.left,list):
            #item1,item2 = val1, val2
            for item,value in zip(node.left,node.right):
                if isinstance(item,ast.SubscriptOperator):
                    raise TypeError_('assignment type not supported',node.line)
                assign = env.set(item.value, self.visit_expression(value, env))
            return assign
        else:
            #name = value
            return env.set(node.left.value,self.visit_expression(node.right, env))

    def visit_getitem(self,node,env):

        data  = self.visit_expression(node.left,env)
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
        # dict[key] = value
        # list[index] = value
        subscript = node.left
        data = self.visit_expression(subscript.left,env)
        key = self.visit_expression(subscript.key,env)
        if node.test:
            test_pass = self.visit_expression(node.test,env)
            if test_pass:
                value = self.visit_expression(node.right,env)
            else:
                value = self.visit_expression(node.right2,env)
        else:
            value  = self.visit_expression(node.right,env)
        try:
            data[key] = value
        except IndexError:
            raise IndexError_('assignment index out of range')
        except TypeError as e:
            raise TypeError_(e,node.line)

    def visit_objcall (self,node,env):
        # name.attr()
        # obj.attr
        obj = self.visit_expression(node.obj,env)
        attr = node.attr
        args = [self.visit_expression(n,env) for n in node.args]
        func = getattr(obj,attr,None)
        if not func:
            raise AttributeError_(f'{obj.__class__.__name__} object has no atrribute "{attr}',node.line)
        try:
            return func(*args) if callable(func) else func
        except TypeError as e:
            raise TypeError_(e,node.line)

    def visit_try(self,node,env):

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
                # raise exception that occurs in try block and catch block
                errors.append(str(x))
                f = '\n\n'+errors[0] +'\n'*2
                s = 'during handling above exception another exception occurs'+'\n'*2+ errors[1]
                raise AbrvalgError(f+s,node.line)
        return body

    def visit_identifier(self,node, env):
        name = node.value
        val = env.get(name)
        if val is None:
            raise NameError_('NameError: Name "{}" is not defined'.format(name),node.line)
        return val

    def visit_match(self,node, env):
        test = self.visit_expression(node.test, env)
        for pattern in node.patterns:
            if self.visit_expression(pattern.pattern, env) == test:
                return self.visit_statements(pattern.body, env)
        if node.else_body is not None:
            return self.visit_statements(node.else_body, env)

    def visit_while_loop(self,node, env):
        while self.visit_expression(node.test, env):
            try:
                self.visit_statements(node.body, env)
            except Break:
                break
            except Continue:
                continue

    def visit_for_loop(self,node, env):
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
        if node.test:
            test = self.visit_expression(node.test,env)
            if test: # test return True
                raise Break()
            return
        raise Break()

    def visit_continue(self,node,env,*args):
        if node.test:
            test = self.visit_expression(node.test,env)
            if test:
                raise Continue()
            return
        raise Continue()

    def visit_function_declaration(self,node, env):
        return env.set(node.name, node)


    def visit_call(self,node, env):
        function = env.get(node.name)
        if function is None:
            raise NameError_('NameError: Name "{}" is not defined'.format(node.name),node.line) 
        if isinstance(function,ast.Function):
            function.check_args(node)
            builtin = False
        elif isinstance (function,Builtins):
            args = [self.visit_expression(arg, env) for arg in node.arguements]
            kwargs = {k:self.visit_expression(v, env) for k, v in node.keywords.items()}
            function.check_args(node)
            try:
                return function.callback(*args,**kwargs)
            except Exception as e:
                raise TypeError_(e,node.line)
        expect = len(function.params)
        given = len(node.arguements)
        if expect != given:
            raise TypeError_('TypeError: {}() takes {} positional argument but {} were given '.format(function.name,expect, given),node.line)
        m = [*node.arguements]
        args = dict(zip(function.params, [self.visit_expression(node, env) for node in m]))

        if isinstance(function,ast.Function):
            call_env = Environment(env, args)
            kwargs = function.keywords.items()
            # set default keywords to env
            for k,v in kwargs:
                v = self.visit_expression(v,env)
                call_env.set(k,v)
            for k,v in node.keywords.items():
                # set keywords in function call to override
                # default value in function defination
                v = self.visit_expression(v,env)
                call_env.set(k,v)
            try:
                self.visit_statements(function.body, call_env)
            except Return as ret:
                return ret.value
            else:
                # no return in the function
                return "None"

    def visit_array(self,node, env):
        l = [self.visit_expression(item, env) for item in node.items]
        return List(l)


    def visit_dict(self,node, env):
        d = {key.value: self.visit_expression(value, env) for key, value in node.items}
        return Dict(d)



    def visit_return(self,node, env):
        exp = self.visit_expression(node.value, env) if node.value is not None else None
        raise Return(exp)


    def visit_condition(self,node, env):
        if self.visit_expression(node.test, env):
            return self.visit_statements(node.if_body, env)

        for cond in node.elifs:
            if self.visit_expression(cond.test, env):
                return self.visit_statements(cond.body, env)

        if node.else_body is not None:
            return self.visit_statements(node.else_body, env)

    def visit_binary_operator(self,node, env):

        left, right = self.visit_expression(node.left, env), self.visit_expression(node.right, env)
        if node.operator in Operators.simple_operations:
            return Operators.simple_operations[node.operator](left,right)
        elif node.operator in Operators.comaprism:
            return Operators.comaprism[node.operator](left,right)

        else:
            raise Exception('Invalid operator {}'.format(node.operator))

    def visit_logical(self,node,env):
        left = self.visit_expression(node.left,env)
        right = self.visit_expression(node.right,env)
        return Operators.logical[node.operator](left,right)

    def visit_not(self,node,env):
        right = self.visit_expression(node.right,env)
        return not right

    def visit_foreach(self,node,env):
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
        module = node.module
        alias = node.alias
        try:
           mod = importlib.import_module(module)
        except ImportError:
            raise TypeError_('couldn\'t find module,%s'%module,node.line)
        name = alias or module # name to use in d environment if alisa is given use it else module name
        return env.set(name,mod)




    
