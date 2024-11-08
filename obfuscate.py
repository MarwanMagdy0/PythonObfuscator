import ast
import random
import string
import astunparse

import builtins
random.seed(0)

def random_name(length=40):
    return ''.join(random.choices(string.ascii_letters, k=length))

def create_mapper(class_and_function_names: set, imported_modules: set, global_variables: set):
    mapper = {}
    for imported_module in imported_modules:
        if imported_module in class_and_function_names:
            mapper[imported_module] = random_name()
            class_and_function_names.remove(imported_module)
        elif imported_module in global_variables:
            mapper[imported_module] = random_name()
            global_variables.remove(imported_module)
        else:
            mapper[imported_module] = imported_module
    
    for class_and_function_name in class_and_function_names:
        mapper[class_and_function_name] = random_name()
    
    for var in global_variables:
        mapper[var] = random_name()
    
    return mapper


class ObfuscateMasters(ast.NodeTransformer):
    def __init__(self):
        super().__init__()
        self.class_and_function_names = set()
        self.imported_modules         = set()
        self.global_variables         = set()

    def visit_Assign(self, node):
        # Only consider top-level assignments (global variables)
        if isinstance(node, ast.Assign):
            for target in node.targets:
                # We are interested in Name nodes at the top level (global scope)
                if isinstance(target, ast.Name):
                    self.global_variables.add(target.id)
        
        # Continue visiting other nodes
        self.generic_visit(node)
        return node


    def visit_FunctionDef(self, node):
        if not node.name.startswith("__") and not node.name.endswith("__"):
            self.class_and_function_names.add(node.name)
        return node
    
    def visit_ClassDef(self, node):
        self.class_and_function_names.add(node.name)
        self.generic_visit(node)
        return node

    def visit_ImportFrom(self, node):
        for alias in node.names:
            self.imported_modules.add(alias.name)
        return node

    def visit_Import(self, node):
        for alias in node.names:
            self.imported_modules.add(alias.name)
        return node

class ObfuscateNames(ast.NodeTransformer):
    def __init__(self,class_and_function_names, imported_modules, global_variables, mapper):
        super().__init__()
        self.class_and_function_names = class_and_function_names
        self.imported_modules         = imported_modules
        self.global_variables         = global_variables
        self.mapper                   = mapper
        self.is_comprehension = False
        self.class_attrs = set()
        self.arguments = {}

    def visit_FunctionDef(self, node):
        print("\n*********visit function*********")
        if node.name in self.mapper:
            node.name = self.mapper[node.name]
        for arg in node.args.args:
            print(arg.arg, "->", arg.lineno)
            if self.arguments.get(arg.arg) is None:
                self.arguments[arg.arg] = random_name()
                arg.arg = self.arguments[arg.arg]
        
        if node.args.vararg:
            print(node.args.vararg.arg)
        if node.args.kwarg:
            print(node.args.kwarg.arg)
        self.generic_visit(node)
        return node
    
    def visit_Lambda(self, node):
        for arg in node.args.args:
            print(arg.arg, "->", arg.lineno)
        self.generic_visit(node)
        return node
    
    def visit_ClassDef(self, node):
        print("\n*********visit class*********")
        # Reset class-specific attributes at the beginning of each class
        self.class_attrs = set()
        if node.name in self.mapper:
            node.name = self.mapper[node.name]
        # Collect all attributes and methods defined directly in this class
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                self.class_attrs.add(item.name)
            elif isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        self.class_attrs.add(target.id)
            # elif isinstance(item, ast.AnnAssign):
            #     if isinstance(item.target, ast.Name):
            #         self.class_attrs.add(item.target.id)

        # print(self.class_attrs)
        self.generic_visit(node)
        return node
    
    def visit_Name(self, node):
        print("\n*********visit Name*********")
        if isinstance(node.ctx, (ast.Load, ast.Store)):
            print(node.id)
            if node.id in dir(builtins):
                return node
            if node.id in self.class_and_function_names or node.id in self.imported_modules or node.id in self.global_variables:
                node.id = self.mapper[node.id]
            else:
                if self.arguments.get(node.id) is None:
                    self.arguments[node.id] = random_name()
                node.id = self.arguments[node.id]
            
        return node

    def visit_ListComp(self, node):
        self.is_comprehension = True
        node.elt = self.visit(node.elt)
        self.generic_visit(node)
        return node

    def visit_Call(self, node):
        print("\n*********visit call*********")
        if isinstance(node.func, ast.Attribute):
            print(node.func.attr)
            if node.func.attr in self.class_and_function_names or node.func.attr in self.imported_modules:
                node.func.attr = self.mapper[node.func.attr]
        return self.generic_visit(node)

    def visit_Attribute(self, node):
        print("\n*********visit attribute*********")
        print(node.attr)
        if self.arguments.get(node.attr) is None:
            self.arguments[node.attr] = random_name()
            node.attr = self.arguments[node.attr]
        return self.generic_visit(node)

    def visit_ImportFrom(self, node):
        for alias in node.names:
            if alias.name in self.headers_map:
                alias.name = self.headers_map[alias.name]
        return node


def obfuscate_code(file_path):
    with open(file_path, "r") as file:
        tree = ast.parse(file.read())

    obfuscator = ObfuscateMasters()
    obfuscated_tree = obfuscator.visit(tree)
    mapper = create_mapper(obfuscator.class_and_function_names, obfuscator.imported_modules, obfuscator.global_variables)
    print(mapper)
    fully_obfsucated = ObfuscateNames(obfuscator.class_and_function_names, obfuscator.imported_modules, obfuscator.global_variables, mapper)
    fully_obfsucated.visit(obfuscated_tree)

    ast.fix_missing_locations(obfuscated_tree)
    obfuscated_code = astunparse.unparse(tree)
    return obfuscated_code

if __name__ == "__main__":
    file_path = "merged_output.py"  # Input Python file you want to obfuscate
    obfuscated_code = obfuscate_code(file_path)

    # Write the obfuscated code to a new file
    with open("obfuscated_output.py", "w") as outfile:
        outfile.write(obfuscated_code)
    print("Obfuscated code written to 'obfuscated_output.py'")
