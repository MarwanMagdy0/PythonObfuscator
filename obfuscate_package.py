from obfuscate import ObfuscateMasters, ObfuscateNames, ast, astunparse, create_mapper
import os
import shutil

def get_all_files_in_directory(root_dir, output_dir="obfuscated_files"):
    # Initialize an empty list to store Python file paths
    all_python_files = []

    # Walk through all directories and files in the root directory
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for dirname in dirnames.copy():
            if dirname.startswith('.') or dirname == '__pycache__':
                dirnames.remove(dirname)

        # Calculate the relative path for the output directory
        relative_path = os.path.relpath(dirpath, root_dir)
        output_path = os.path.join(output_dir, relative_path)

        # Ensure the output directory structure matches the input structure
        os.makedirs(output_path, exist_ok=True)

        for filename in filenames:
            full_file_path = os.path.join(dirpath, filename)

            if filename.endswith(".py"):
                # Append Python files to the list for further processing
                all_python_files.append(full_file_path)
            else:
                # Copy non-Python files directly to the output directory
                print(f"Copying file: {full_file_path}")
                shutil.copy(full_file_path, os.path.join(output_path, filename))

    return all_python_files


def obfuscate_code(root_dir, ignore_words=[]):
    files = get_all_files_in_directory(root_dir)
    class_and_function_names = set()
    imported_modules = set()
    global_variables = set()
    each_file_tree = {}
    for file in files:
        if not os.path.isfile(file):
            continue

        with open(file, "r") as f:
            tree = ast.parse(f.read())
        obfuscate_masters = ObfuscateMasters()
        obfuscate_masters.visit(tree)
        class_and_function_names.update(obfuscate_masters.class_and_function_names)
        imported_modules.update(obfuscate_masters.imported_modules)
        global_variables.update(obfuscate_masters.global_variables)
        each_file_tree[file] = tree

    os.makedirs("obfuscated_files", exist_ok=True)
    mapper = create_mapper(class_and_function_names, imported_modules, global_variables)
    print(mapper)
    for file in files:
        print("[Start obfuscating]", file)
        if not os.path.isfile(file):
            continue

        tree = each_file_tree[file]
        fully_obfsucated = ObfuscateNames(class_and_function_names, imported_modules, global_variables, mapper)
        fully_obfsucated.visit(tree)
        ast.fix_missing_locations(tree)
        obfuscated_code = astunparse.unparse(tree)
        relative_path = os.path.relpath(file, root_dir)
        output_path = os.path.join("obfuscated_files", relative_path)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as outfile:
            outfile.write(obfuscated_code)

        print(f"Obfuscated file written to: {output_path}")

root_dir = "/media/marwan/01DA974290394900/Python_Projects/Qt/QPaint_HowToUse/omar"
ignore_words = ["setupUi", "paintEvent"]
obfuscate_code(root_dir, ignore_words)