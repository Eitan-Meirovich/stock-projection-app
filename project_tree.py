import os
import argparse
from pathlib import Path

def display_tree(directory, exclude_dirs=None, prefix=''):
    if exclude_dirs is None:
        exclude_dirs = {'.git', '__pycache__', 'venv', 'node_modules'}
    
    result = []
    paths = sorted(Path(directory).iterdir())
    
    for index, path in enumerate(paths):
        if path.name in exclude_dirs:
            continue
            
        is_last = index == len(paths) - 1
        connector = '└──' if is_last else '├──'
        
        result.append(f'{prefix}{connector} {path.name}')
        
        if path.is_dir():
            extension = '    ' if is_last else '│   '
            result.extend(display_tree(path, exclude_dirs, prefix + extension))
    
    return result

def save_tree_to_file(tree_content, output_file):
    output_path = Path(output_file)
    output_path.write_text('\n'.join(tree_content), encoding='utf-8')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Display directory tree structure')
    parser.add_argument('--output', '-o', help='Output file path')
    args = parser.parse_args()

    current_dir = os.getcwd()
    header = f'Project structure for: {current_dir}\n'
    tree_content = [header] + display_tree(current_dir)
    
    print('\n'.join(tree_content))
    
    if args.output:
        save_tree_to_file(tree_content, args.output)
        print(f'\nTree structure saved to: {args.output}')