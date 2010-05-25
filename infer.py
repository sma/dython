import ast, astutils

class Kind:
    @staticmethod
    def tuple(*kinds):
        return Tuple(kinds)
    
    @staticmethod
    def list(kind):
        return List(kind)
    
    @staticmethod
    def func(kind):
        return Func(kind)
    
    def __lt__(self, other):
        raise ValueError
        
class Void(Kind):
    def __str__(self):
        return "void"

class Any(Kind):
    def __str__(self):
        return "any"
    
class Int(Kind):
    def __str__(self):
        return "int"

class Str(Kind):
    def __str__(self):
        return "str"

class Tuple(Kind):
    def __init__(self, kinds):
        self.kinds = kinds
    
    def __str__(self):
        return "(%s)" % ", ".join(str(kind for kind in self.kinds))

    def __eq__(self, other):
        return type(self) == type(other) and self.kinds == other.kinds

class List(Kind):
    def __init__(self, kind):
        self.kind = kind
    
    def __str__(self):
        return "[%s]" % self.kind

    def __eq__(self, other):
        return type(self) == type(other) and self.kind == other.kind

class Func(Kind):
    def __init__(self, kind):
        self.kind = kind
    
    def __str__(self):
        return "%s()" % self.kind
    
    def __eq__(self, other):
        return type(self) == type(other) and self.kind == other.kind

Kind.void = Void()
Kind.any = Any()
Kind.int = Int()
Kind.str = Str()

def join_kinds(*kinds):
    if not kinds:
        return Kind.list(Kind.any)
    kind = kinds[0]
    for k in kinds[1:]:
        if k != kind:
            return Kind.list(Kind.any)
    return Kind.list(kind)

class Scope:
    def __init__(self, outer=None):
        self.outer = outer
        self.bindings = {}
    
    def __getitem__(self, name):
        try:
            return self.bindings[name]
        except KeyError:
            return self.outer[name]
    
    def __setitem__(self, name, kind):
        self.bindings[name] = kind

@astutils.inject_into(ast)
class InferMethods:
    def Module_infer(self, scope):
        for stmt in self.body:
            stmt.infer(scope)
        self.kind = self.body[-1].kind
    
    def Expr_infer(self, scope):
        self.value.infer(scope)
        self.kind = self.value.kind
    
    def Num_infer(self, scope):
        self.kind = Kind.int
        
    def Str_infer(self, scope):
        self.kind = Kind.str

    def Tuple_infer(self, scope):
        for elt in self.elts:
            elt.infer(scope)
        self.kind = Kind.tuple(*(elt.kind for elt in self.elts))
    
    def List_infer(self, scope):
        for elt in self.elts:
            elt.infer(scope)
        self.kind = join_kinds(*(elt.kind for elt in self.elts))
    
    def BinOp_infer(self, scope):
        self.left.infer(scope)
        self.right.infer(scope)
        self.kind = self.op.infer_op(self.left.kind, self.right.kind)
    
    def Add_infer_op(self, left_kind, right_kind):
        if left_kind == Kind.int and right_kind == Kind.int:
            return Kind.int
        if left_kind == Kind.str and right_kind == Kind.str:
            return Kind.str
        return Kind.void
    
    def Assign_infer(self, scope):
        self.value.infer(scope)
        self.targets[0].bind(scope, self.value.kind)
        self.kind = Kind.void
    
    def Name_bind(self, scope, kind):
        scope[self.id] = kind
    
    def Name_infer(self, scope):
        self.kind = scope[self.id]
    
    def Call_infer(self, scope):
        self.func.infer(scope)
        for arg in self.args:
            arg.infer(scope)
        self.kind = self.func.kind.kind
