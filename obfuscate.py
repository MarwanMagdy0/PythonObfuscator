import ast
import random
import string
import astor
random.seed(0)
class ObfuscateMasters(ast.NodeTransformer):
    def __init__(self):
        super().__init__()
        self.name_map = {}
        self.imported_modules = set()
        self.is_comprehension = False

    def random_name(self, length=40):
        return ''.join(random.choices(string.ascii_letters, k=length))

    def obfuscate_name(self, original_name):
        if original_name.startswith('__') and original_name.endswith('__'):
            return original_name
        
        if original_name in self.imported_modules:
            return original_name
        
        if original_name not in self.name_map:
            new_name = self.random_name()
            while new_name in self.name_map.values():
                new_name = self.random_name()
            self.name_map[original_name] = new_name
        return self.name_map[original_name]


    def visit_FunctionDef(self, node):
        node.name = self.obfuscate_name(node.name)
        return node
    
    def visit_ClassDef(self, node):
        node.name = self.obfuscate_name(node.name)

        self.generic_visit(node)
        return node

    def visit_ImportFrom(self, node):
        for alias in node.names:
            self.imported_modules.add(alias.name)
        return node

class ObfuscateNames(ast.NodeTransformer):
    def __init__(self, name_map, imported_modules):
        super().__init__()
        self.name_map = name_map
        self.imported_modules = imported_modules
        self.is_comprehension = False

    def random_name(self, length=40):
        return ''.join(random.choices(string.ascii_letters, k=length))

    def obfuscate_name(self, original_name):
        if original_name.startswith('__') and original_name.endswith('__'):
            return original_name
        
        if original_name in self.imported_modules:
            return original_name
        
        if original_name not in self.name_map:
            new_name = self.random_name()
            while new_name in self.name_map.values():
                new_name = self.random_name()
            self.name_map[original_name] = new_name
        return self.name_map[original_name]

    def visit_FunctionDef(self, node):
        node.args.args = [
            ast.arg(arg=self.obfuscate_name(arg.arg), annotation=arg.annotation)
            for arg in node.args.args
        ]
        self.generic_visit(node)
        return node
    
    def visit_Lambda(self, node):
        node.args.args = [
            ast.arg(arg=self.obfuscate_name(arg.arg), annotation=arg.annotation)
            for arg in node.args.args
        ]
        self.generic_visit(node)
        return node
    
    def visit_ClassDef(self, node):

        self.generic_visit(node)
        return node

    def visit_Name(self, node):
        if node.id in self.name_map:
            node.id = self.name_map[node.id]
        elif isinstance(node.ctx, (ast.Store)):
            node.id = self.obfuscate_name(node.id)

        elif self.is_comprehension:
            node.id = self.obfuscate_name(node.id)
            self.is_comprehension = False

        return node

    def visit_ListComp(self, node):
        self.is_comprehension = True
        node.elt = self.visit(node.elt)
        self.generic_visit(node)
        return node

    def visit_Attribute(self, node):
        if node.attr in self.name_map:
            node.attr = self.name_map[node.attr]
        return self.generic_visit(node)

    def visit_ImportFrom(self, node):
        for alias in node.names:
            if alias.name in self.name_map:
                alias.name = self.name_map[alias.name]
        return node


def obfuscate_code(file_path):
    with open(file_path, "r") as file:
        tree = ast.parse(file.read())

    obfuscator = ObfuscateMasters()
    obfuscated_tree = obfuscator.visit(tree)
    print(obfuscator.imported_modules)
    fully_obfsucated = ObfuscateNames(obfuscator.name_map, obfuscator.imported_modules)
    fully_obfsucated.visit(obfuscated_tree)

    ast.fix_missing_locations(obfuscated_tree)
    obfuscated_code = astor.to_source(obfuscated_tree, add_line_information=True)
    return obfuscated_code

# Example usage:
file_path = "merged_output.py"  # Input Python file you want to obfuscate
obfuscated_code = obfuscate_code(file_path)

# Write the obfuscated code to a new file
with open("obfuscated_output.py", "w") as outfile:
    outfile.write(obfuscated_code)
print("Obfuscated code written to 'obfuscated_output.py'")
