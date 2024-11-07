import ast
import os

def remove_main_block(file_path):
    with open(file_path, "r") as file:
        tree = ast.parse(file.read())

    # List of lines in the file
    with open(file_path, "r") as file:
        lines = file.readlines()

    # Locate and remove `if __name__ == "__main__"` block
    new_lines = lines.copy()
    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            # Check for __name__ == "__main__" condition
            if (
                isinstance(node.test, ast.Compare)
                and isinstance(node.test.left, ast.Name)
                and node.test.left.id == "__name__"
                and any(isinstance(op, ast.Eq) for op in node.test.ops)
                and any(isinstance(comp, ast.Constant) and comp.value == "__main__"
                        for comp in node.test.comparators)
            ):
                # Remove lines for the main block (using line numbers)
                start_line = node.lineno - 1
                end_line = node.end_lineno
                new_lines[start_line:end_line] = []  # Remove lines

    return "".join(new_lines)


def generate_single_file(input_files, output_file):
    with open(output_file, "w") as outfile:
        for file_path in input_files:
            code_without_main = remove_main_block(file_path)
            outfile.write("# From file: " + os.path.basename(file_path) + "\n")
            outfile.write(code_without_main + "\n")
            outfile.write("\n#" + "-" * 40 + "\n\n")  # Separator between files

# Example usage:
input_files = ["file1.py", "file2.py", "file3.py"]
output_file = "merged_output.py"
generate_single_file(input_files, output_file)
print(f"Generated {output_file} without `if __name__ == '__main__'` blocks.")
