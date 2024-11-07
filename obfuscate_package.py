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

root_dir = "/media/marwan/01DA974290394900/Python_Projects/Qt/QPaint_HowToUse/omar"
files = get_all_files_in_directory(root_dir)
print(files)
all_golobals = {}
each_file_imports = []
each_file_tree = {}
for file in files:
    if not os.path.isfile(file):
        continue

    with open(file, "r") as f:
        tree = ast.parse(f.read())
    obfuscate_masters = ObfuscateMasters()
    obfuscate_masters.visit(tree)
    all_golobals.update(obfuscate_masters.name_map)
    each_file_imports.extend(obfuscate_masters.imported_modules)
    each_file_tree[file] = tree

print(all_golobals)
print(each_file_imports)
os.makedirs("obfuscated_files", exist_ok=True)
for file in files:
    if not os.path.isfile(file):
        continue

    tree = each_file_tree[file]
    
    fully_obfsucated = ObfuscateNames(all_golobals, each_file_imports)
    fully_obfsucated.visit(tree)

    ast.fix_missing_locations(tree)
    obfuscated_code = astor.to_source(tree, add_line_information=True)
    # Extract the relative path of the file, excluding the root directory
    relative_path = os.path.relpath(file, root_dir)

    # Create the necessary directories in the output directory
    output_path = os.path.join("obfuscated_files", relative_path)

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Write the obfuscated code to the corresponding file in the new directory
    with open(output_path, "w") as outfile:
        outfile.write(obfuscated_code)

    print(f"Obfuscated file written to: {output_path}")