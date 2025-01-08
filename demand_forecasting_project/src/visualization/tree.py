import os

def generate_tree_structure(root_dir, output_file):
    with open(output_file, 'w') as f:
        for dirpath, dirnames, filenames in os.walk(root_dir):
            # Calcula la profundidad del directorio para agregar indentación
            depth = dirpath.replace(root_dir, "").count(os.sep)
            indent = " " * 4 * depth
            f.write(f"{indent}{os.path.basename(dirpath)}/\n")
            subindent = " " * 4 * (depth + 1)
            for filename in filenames:
                f.write(f"{subindent}{filename}\n")

# Cambia el directorio raíz y el archivo de salida según tu configuración
root_directory = "."  # Directorio actual
output_file = "estructura_directorio.txt"

generate_tree_structure(root_directory, output_file)
print(f"Estructura guardada en {output_file}")
