import unittest
import ast
from infer import Scope, Kind

global_scope = Scope()
global_scope["range"] = Kind.func(Kind.list(Kind.int))

def infer(s):
    a = ast.parse(s)
    print(ast.dump(a))
    a.infer(Scope(global_scope))
    return a.kind

class TestInfer(unittest.TestCase):
    def test_literals(self):
        assert infer("1") == Kind.int
        assert infer("''") == Kind.str
    
    def test_tuples(self):
        assert infer("()") == Kind.tuple()
        assert infer("(1,'')") == Kind.tuple(Kind.int, Kind.str)
    
    def test_lists(self):
        assert infer("[]") == Kind.list(Kind.any)
        assert infer("[1, 2]") == Kind.list(Kind.int)
        assert infer("[1, '']") == Kind.list(Kind.any)
        assert infer("['a']") == Kind.list(Kind.str)
    
    def test_operators(self):
        assert infer("1 + 2") == Kind.int

    def test_assignments(self):
        assert infer("a = 1; a") == Kind.int
    
    def test_builtin_functions(self):
        assert infer("a = range(10); a") == Kind.list(Kind.int)

if __name__ == '__main__':
    unittest.main()