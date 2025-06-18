import os

def generate_project_summary(root_dir, output_file="project-sum.txt"):
    # List of directories to skip
    skip_dirs = [".git", "node_modules", "__pycache__", "mysql"]

    # Function to recursively build the directory structure
    def build_structure(path, prefix=""):
        entries = []
        for item in sorted(os.listdir(path)):
            # Skip directories in the skip list
            if item in skip_dirs:
                continue
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                entries.append(f"{prefix}├── {item}/")
                entries.extend(build_structure(item_path, prefix + "│   "))
            else:
                entries.append(f"{prefix}├── {item}")
        return entries

    # Build the structure starting from the specified root directory
    structure = [f"{os.path.basename(root_dir)}/"]
    structure.extend(build_structure(root_dir, "│   "))

    # Write the structure to the output file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(structure))


# Specify the root directory (parent directory of the script)
root_directory = os.getcwd()
generate_project_summary(root_directory)
print(f"Project summary has been generated in {root_directory}/project-sum.txt")