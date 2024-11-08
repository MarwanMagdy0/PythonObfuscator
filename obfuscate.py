import ast
import random
import string
import astunparse

import builtins
random.seed(0)
class ObfuscateMasters(ast.NodeTransformer):
    def __init__(self, ignore_words=[]):
        super().__init__()
        self.headers_map = {}
        self.imported_modules = set()
        self.is_comprehension = False
        self.ignore_words = ignore_words

    def random_name(self, length=40):
        return ''.join(random.choices(string.ascii_letters, k=length))

    def obfuscate_name(self, original_name):
        if original_name.startswith('__') and original_name.endswith('__'):
            return original_name
        
        if original_name in self.imported_modules:
            return original_name
        
        if original_name in self.ignore_words:
            return original_name
        
        if original_name in self.headers_map:
            print(original_name)
            return original_name
        
        if original_name not in self.headers_map:
            new_name = self.random_name()
            while new_name in self.headers_map.values():
                new_name = self.random_name()
            self.headers_map[original_name] = new_name
        return self.headers_map[original_name]

    def visit_Assign(self, node):
        # Only consider top-level assignments (global variables)
        if isinstance(node, ast.Assign):
            for target in node.targets:
                # We are interested in Name nodes at the top level (global scope)
                if isinstance(target, ast.Name):
                    target.id = self.obfuscate_name(target.id)
        
        # Continue visiting other nodes
        self.generic_visit(node)
        return node


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
    def __init__(self, headers_map, imported_modules, ignore_words=[]):
        super().__init__()
        self.headers_map = headers_map
        self.name_map = {}
        self.imported_modules = imported_modules
        self.ignore_words = ignore_words
        self.is_comprehension = False
        self.class_attrs = set()

    def random_name(self, length=40):
        return ''.join(random.choices(string.ascii_letters, k=length))

    def obfuscate_name(self, original_name):
        if original_name.startswith('__') and original_name.endswith('__'):
            return original_name
        
        if original_name in self.imported_modules:
            return original_name
        
        if original_name in self.ignore_words:
            return original_name
        
        if original_name in dir(builtins):
            return original_name
        
        if original_name in self.headers_map.values():
            return original_name
        
        if original_name in self.headers_map:
            # print(original_name)
            return self.headers_map[original_name]

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
        # Reset class-specific attributes at the beginning of each class
        self.class_attrs = set()
        
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
        if node.id in self.name_map:
            node.id = self.name_map[node.id]

        elif node.id in self.headers_map:
            node.id = self.headers_map[node.id]

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
        if isinstance(node.value, ast.Name) and (node.attr in self.name_map or node.attr in self.headers_map):
            if self.headers_map.get(node.attr) in self.class_attrs:
                node.attr = self.headers_map[node.attr]
            elif node.value.id in self.headers_map:
                node.attr = self.headers_map[node.value.id]
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
    print(obfuscator.headers_map)
    fully_obfsucated = ObfuscateNames(obfuscator.headers_map, obfuscator.imported_modules)
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
