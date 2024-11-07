from obfuscate import ObfuscateMasters, ObfuscateNames, ast, astor
import os

def get_all_files_in_directory(root_dir):
    # Initialize an empty list to store file paths
    all_files = []

    # Walk through all directories and files in the root directory
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # For each file in the directory, append its full path to the list
        for filename in filenames:
            if filename.endswith(".py"):
                full_file_path = os.path.join(dirpath, filename)
                all_files.append(full_file_path)
    
    return all_files

def obfuscate_code(root_dir, ignore_words=[]):
    files = get_all_files_in_directory(root_dir)
    all_golobals = {}
    each_file_imports = []
    each_file_tree = {}
    for file in files:
        if not os.path.isfile(file):
            continue

        with open(file, "r") as f:
            tree = ast.parse(f.read())
        obfuscate_masters = ObfuscateMasters(ignore_words)
        obfuscate_masters.visit(tree)
        all_golobals.update(obfuscate_masters.name_map)
        each_file_imports.extend(obfuscate_masters.imported_modules)
        each_file_tree[file] = tree

    os.makedirs("obfuscated_files", exist_ok=True)
    for file in files:
        if not os.path.isfile(file):
            continue
        tree = each_file_tree[file]
        fully_obfsucated = ObfuscateNames(all_golobals, each_file_imports, ignore_words)
        fully_obfsucated.visit(tree)
        ast.fix_missing_locations(tree)
        obfuscated_code = astor.to_source(tree, add_line_information=True)
        relative_path = os.path.relpath(file, root_dir)
        output_path = os.path.join("obfuscated_files", relative_path)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as outfile:
            outfile.write(obfuscated_code)
        print(f"Obfuscated file written to: {output_path}")

root_dir = "/media/marwan/01DA974290394900/Python_Projects/Qt/QPaint_HowToUse/omar"
ignore_words = ["setupUi", "paintEvent"]
obfuscate_code(root_dir, ignore_words)