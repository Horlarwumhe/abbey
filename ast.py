from dataclasses import InitVar, dataclass
from typing import Any, ClassVar, Tuple

from abbey.errors import TypeError_


@dataclass(repr=False, eq=False)
class Node:
    fields: ClassVar[Tuple[str, ...]] = ()
    exclude: ClassVar[Tuple[str, ...]] = ()  # excluded fields in str representation

    def __str__(self):
        s = f"<{self.__class__.__name__} "
        for name in self.fields:
            if name in self.exclude:
                continue
            try:
                # Handle the exception; don't use getattr(self, name, None),
                # since an attribute can legitimately have a None value.
                value = getattr(self, name)
            except AttributeError:
                continue
            if hasattr(value, 'value'):
                value = value.value
            s += ' {} = "{}",'.format(name, value)
        s += ">"
        return s

    def __repr__(self):
        return str(self)


@dataclass(repr=False, eq=False)
class Number(Node):
    value: Any
    line: Any
    _name: ClassVar[str] = 'num'
    fields: ClassVar[Tuple[str, ...]] = ('value', 'line')


@dataclass(repr=False, eq=False)
class String(Node):
    value: Any
    line: Any
    _name: ClassVar[str] = 'str'
    fields: ClassVar[Tuple[str, ...]] = ('value', 'line')


@dataclass(repr=False, eq=False)
class Identifier(Node):
    value: Any
    line: Any
    _name: ClassVar[str] = 'id'
    fields: ClassVar[Tuple[str, ...]] = ('value', 'line')


@dataclass(repr=False, eq=False)
class Function(Node):
    name: Any
    arguements: Any
    keywords: Any
    body: Any
    line: Any
    _name: ClassVar[str] = 'function'
    fields: ClassVar[Tuple[str, ...]] = ("name", "arguements", "keywords", "body", "line")
    exclude: ClassVar[Tuple[str, ...]] = ('body',)

    def check_args(self, call):
        self.parser_kwargs(call)

    def parser_kwargs(self, call):
        for k in call.keywords:
            if k not in self.keywords:
                raise TypeError_(f"TypeError_ ,{call.name}() got unexpected keyword arguments {k}", call.line)


@dataclass(repr=False, eq=False)
class Assignment(Node):
    left: Any
    right: Any
    test: Any
    right2: Any
    line: Any
    _name: ClassVar[str] = 'assign'
    fields: ClassVar[Tuple[str, ...]] = ('left', 'right', 'test', 'right2', 'line')


@dataclass(repr=False, eq=False)
class BinaryOperator(Node):
    operator: Any
    left: Any
    right: Any
    line: Any
    fields: ClassVar[Tuple[str, ...]] = ('operator', 'left', 'right', 'line')


@dataclass(repr=False, eq=False)
class NotOperator(Node):
    right: Any
    line: Any
    fields: ClassVar[Tuple[str, ...]] = ('right', 'line')


@dataclass(repr=False, eq=False)
class Call(Node):
    name: Any
    arguements: Any
    keywords: Any
    line: Any
    _name: ClassVar[str] = 'call'
    fields: ClassVar[Tuple[str, ...]] = ("name", "arguements", "keywords", "line")


@dataclass(repr=False, eq=False)
class Condition(Node):
    test: Any
    if_body: Any
    elifs: Any
    else_body: Any
    line: Any
    _name: ClassVar[str] = 'if'
    fields: ClassVar[Tuple[str, ...]] = ('test', 'if_body', 'elifs', 'else_body', 'line')

    def __str__(self):
        return "<{}, test = {}, ifbody = {},line = {} else_body={}".format(
            self.__class__.__name__, self.test, len(self.if_body), self.line, bool(self.else_body)
        )


@dataclass(repr=False, eq=False)
class ConditionElif(Node):
    test: Any
    body: Any
    line: Any
    _name: ClassVar[str] = 'elif'
    fields: ClassVar[Tuple[str, ...]] = ('test', 'body', 'line')
    exclude: ClassVar[Tuple[str, ...]] = ('body',)


@dataclass(repr=False, eq=False)
class Match(Node):
    test: Any
    patterns: Any
    else_body: Any
    line: Any
    _name: ClassVar[str] = 'match'
    fields: ClassVar[Tuple[str, ...]] = ('test', 'patterns', 'else_body', 'line')

    def __str__(self):
        return f"{self.__class__.__name__}, test = {self.test}, pattern = {len(self.patterns)}, line = {self.line}"


@dataclass(repr=False, eq=False)
class MatchPattern(Node):
    pattern: Any
    body: Any
    line: Any
    _name: ClassVar[str] = 'case'
    fields: ClassVar[Tuple[str, ...]] = ('pattern', 'body', 'line')
    exclude: ClassVar[Tuple[str, ...]] = ('body',)


@dataclass(repr=False, eq=False)
class WhileLoop(Node):
    test: Any
    body: Any
    line: Any
    _name: ClassVar[str] = 'while'
    fields: ClassVar[Tuple[str, ...]] = ('test', 'body', 'line')
    exclude: ClassVar[Tuple[str, ...]] = ('body',)


@dataclass(repr=False, eq=False)
class ForLoop(Node):
    var_name: Any
    collection: Any
    body: Any
    line: Any
    _name: ClassVar[str] = 'for'
    fields: ClassVar[Tuple[str, ...]] = ('var_name', 'collection', 'body', 'line')
    exclude: ClassVar[Tuple[str, ...]] = ('body',)


@dataclass(repr=False, eq=False)
class Break(Node):
    test: Any
    line: Any
    _name: ClassVar[str] = 'break'
    fields: ClassVar[Tuple[str, ...]] = ('test', 'line')


@dataclass(repr=False, eq=False)
class Continue(Node):
    test: Any
    line: Any
    _name: ClassVar[str] = 'continue'
    fields: ClassVar[Tuple[str, ...]] = ('test', 'line')


@dataclass(repr=False, eq=False)
class Return(Node):
    value: Any
    line: Any
    _name: ClassVar[str] = 'return'
    fields: ClassVar[Tuple[str, ...]] = ('value', 'line')


@dataclass(repr=False, eq=False)
class Array(Node):
    items: Any
    line: Any
    _name: ClassVar[str] = 'list'
    fields: ClassVar[Tuple[str, ...]] = ('items', 'line')


@dataclass(repr=False, eq=False)
class Dictionary(Node):
    items: Any
    line: Any
    _name: ClassVar[str] = 'dict'
    fields: ClassVar[Tuple[str, ...]] = ('items', 'line')


@dataclass(repr=False, eq=False)
class SubscriptOperator(Node):
    left: Any
    key: Any
    line: Any
    _name: ClassVar[str] = 'subcript'
    fields: ClassVar[Tuple[str, ...]] = ('left', 'key', 'line')


@dataclass(repr=False, eq=False)
class Program(Node):
    body: Any
    line: InitVar[Any] = None

    def __str__(self):
        return "<Programs statements=%s>" % len(self.body)

    def get_node(self, name):
        return [node for node in self.body if node.__class__.__name__.lower() == name]


@dataclass(repr=False, eq=False)
class Objcall(Node):
    obj: Any
    attr: Any
    arguements: Any
    line: Any
    _name: ClassVar[str] = 'objcall'
    fields: ClassVar[Tuple[str, ...]] = ('obj', 'attr', 'arguements', 'line')


@dataclass(repr=False, eq=False)
class Try(Node):
    body: Any
    catch_body: Any
    catch_var: Any
    line: Any
    _name: ClassVar[str] = 'try'
    fields: ClassVar[Tuple[str, ...]] = ('body', 'catch_body', 'catch_var', 'line')
    exclude: ClassVar[Tuple[str, ...]] = ('body', 'catch_body')


@dataclass(repr=False, eq=False)
class ForEach(Node):
    obj: Any
    var_name: Any
    body: Any
    line: Any
    _name: ClassVar[str] = 'foreach'
    fields: ClassVar[Tuple[str, ...]] = ('obj', 'var_name', 'body', 'line')
    exclude: ClassVar[Tuple[str, ...]] = ('body',)


@dataclass(repr=False, eq=False)
class Use(Node):
    module: Any
    alias: Any
    line: Any
    _name: ClassVar[str] = 'use'
    fields: ClassVar[Tuple[str, ...]] = ('module', 'alias', 'line')


@dataclass(repr=False, eq=False)
class Include(Node):
    function: Any
    file: Any
    line: Any
    _name: ClassVar[str] = 'include'
    fields: ClassVar[Tuple[str, ...]] = ('function', 'file', 'line')


@dataclass(repr=False, eq=False)
class LogicalOperator(Node):
    # in, and, or
    left: Any
    right: Any
    operator: Any
    line: Any
    _name: ClassVar[str] = 'logical'
    fields: ClassVar[Tuple[str, ...]] = ('left', 'right', 'operator', 'line')


@dataclass(repr=False, eq=False)
class Class_(Node):
    name: Any
    arguements: Any
    keywords: Any
    body: Any
    line: Any
    env: Any
    _name: ClassVar[str] = 'class'
    fields: ClassVar[Tuple[str, ...]] = ('name', 'arguements', 'keywords', 'body', 'line', 'env')

    def load_env(self):
        for node in self.body:
            if isinstance(node, Assignment):
                self.env[node.left] = node
            elif isinstance(node, Function):
                self.env[node.name] = node
