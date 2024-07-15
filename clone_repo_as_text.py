import os

# Summary:
# This script generates a text file containing the directory structure and contents of all files
# (excluding hidden files and directories, e.g., .git) in a given GitHub repository. This is useful
# for creating text output for AI ingestion.
# The script must be executed from the root directory of the repository.

def print_directory_structure(root_dir):
    """
    Recursively walks through the directory and prints the structure diagram.
    
    Args:
    - root_dir: The root directory to start the walk.
    """
    structure_lines = []
    for root, dirs, files in os.walk(root_dir):
        # Filter out hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        level = root.replace(root_dir, '').count(os.sep)
        indent = ' ' * 4 * (level)
        relative_root = os.path.relpath(root, root_dir)
        if relative_root == '.':
            relative_root = os.path.basename(root_dir)
        structure_lines.append('{}{}/'.format(indent, relative_root))
        
        sub_indent = ' ' * 4 * (level + 1)
        for file in files:
            if not file.startswith('.'):
                structure_lines.append('{}{}'.format(sub_indent, file))
    
    return '\n'.join(structure_lines)

def clone_repo_as_text(root_dir, output_file):
    """
    Recursively walks through the directory and writes the structure and contents of each file
    to the output file, excluding hidden files and directories (those starting with a dot).

    Args:
    - root_dir: The root directory to start the walk.
    - output_file: The file to write the directory structure and contents.
    """
    with open(output_file, 'w') as f_out:
        # Print the directory structure first
        directory_structure = print_directory_structure(root_dir)
        f_out.write("Project Directory Structure:\n")
        f_out.write(directory_structure)
        f_out.write("\n\nContents of Files:\n\n")
        
        for root, dirs, files in os.walk(root_dir):
            # Filter out hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            # Calculate the directory level based on the depth
            level = root.replace(root_dir, '').count(os.sep)
            indent = ' ' * 4 * (level)
            
            # Get the relative path of the current directory
            relative_root = os.path.relpath(root, root_dir)
            if relative_root == '.':
                relative_root = ''
                
            # Write the directory name
            f_out.write('{}{}/\n'.format(indent, relative_root))
            sub_indent = ' ' * 4 * (level + 1)
            
            # Iterate through files in the current directory
            for file in files:
                # Skip hidden files
                if file.startswith('.'):
                    continue
                
                file_path = os.path.join(root, file)
                
                # Write the filename
                f_out.write('{}{}\n'.format(sub_indent, file))
                
                # Write the content of the file
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f_in:
                    f_out.write('{}\n'.format(sub_indent + '-' * len(file)))
                    f_out.write(f_in.read())
                    f_out.write('\n{}{}\n\n'.format(sub_indent, '-' * len(file)))

# Set the root directory to the current directory (assuming the script is executed from the root directory of the repo)
repo_path = '.'

# Determine the name of the root directory
root_dir_name = os.path.basename(os.path.abspath(repo_path))

# Set the output file name based on the root directory name
output_file = f'{root_dir_name}_structure_with_contents.txt'

# Generate and print the directory structure with contents
clone_repo_as_text(repo_path, output_file)

print(f"Output written to {output_file}")
