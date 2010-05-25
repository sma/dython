import ast, astutils

class State:
    def __init__(self, package):
        self.package = package
        self.indent = 0
        self.classes = set()
        
    def pr(self, s="", *args):
        s = s % args
        if s == "}":
            self.indent -= 1
        print("  " * self.indent + s)
        if s.endswith("{"):
            self.indent += 1
    
@astutils.inject_into(ast)
class TranslateMethods:
    def Module_translate(self, state):
        state.pr("package %s;", state.package)
        for stmt in self.body:
            stmt.translate_imports(state)
        for stmt in self.body:
            stmt.translate_classes(state)
            
        state.pr("public class Test {")
        state.pr("public static void main(String[] args) {")
        for stmt in self.body:
            stmt.translate(state)
        state.pr("}")
        state.pr("}")
    
    def stmt_translate_imports(self, state):
        pass
    
    def ImportFrom_translate_imports(self, state):
        for alias in self.names:
            state.pr("import %s.%s;", self.module, alias.name)
            state.classes.add(alias.name)
    
    def stmt_translate_classes(self, state):
        pass
    
    def ClassDef_translate_classes(self, state):
        state.pr("class %s extends %s {" % (self.name, self.bases[0].id))
        for stmt in self.body:
            stmt.translate(state)
        state.pr("}")
    
    def FunctionDef_translate(self, state):
        state.pr("public void %s(%s) {" % (self.name, self.args.translate(state)))
        for stmt in self.body:
            stmt.translate(state)
        state.pr("}")

    def arguments_translate(self, state):
        return ", ".join(arg.translate(state) for arg in self.args)

    def arg_translate(self, state):
        # TODO translate_as_type
        return "%s %s" % (self.annotation.translate(state) if self.annotation else "Object", self.arg)
    
    def Name_translate(self, state):
        if self.id == "self":
            return "this"
        return self.id
    
    def Expr_translate(self, state):
        state.pr(self.value.translate(state) + ";")
    
    def Call_translate(self, state):
        func = self.func.translate(state)
        if func == 'super':
            return func
        if func in state.classes:
            func = "new " + func
        if func == "print":
            func = "System.out.println"
        return "%s(%s)" % (func, ", ".join(arg.translate(state) for arg in self.args))

    def Attribute_translate(self, state):
        return "%s.%s" % (self.value.translate(state), self.attr)
    
    def Assign_translate(self, state):
        value = self.value.translate(state)
        if value.startswith("new "):
            var = value[4:value.index('(')]
        else:
            var = "Object"
        state.pr("%s %s = %s;", var, self.targets[0].translate(state), value)
    
    def Str_translate(self, state):
        return '"%s"' % self.s.replace('\\', '\\\\').replace('"', '\\"')
    
    def ImportFrom_translate(self, state):
        pass
        
    def ClassDef_translate(self, state):
        pass

    def Num_translate(self, state):
        return str(self.n)

    def BinOp_translate(self, state):
        return "%s %s %s" % (self.left.translate(state), self.op.name(), self.right.translate(state))
    
    def Add_name(self):
        return "+"
    
    