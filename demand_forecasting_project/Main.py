import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import subprocess
import os

# Obtener el directorio base (donde se encuentra Main.py)
base_dir = os.path.dirname(os.path.abspath(__file__))

# Definir la lista de scripts en el orden de ejecución con rutas absolutas
scripts = [
    "src/data/hierarchy_map.py",
    "run_processor.py",
    "src/data/Data_groups.py",
    "src/models/Proyecciones.py",
    "src/models/Invierno/Top_Down.py",
    "src/models/Hilos_Verano/Top_Down_Verano_25.py",
    "src/models/Bebé/Top_Down_25.py",
    "Consolidado_resultados.py",
    "src/data/Demanda_real.py",
    "merged_data.py",
    "src/Descarga_Stock.py",
    "src/flow_details.py"
]

# Ejecutar cada script
for script in scripts:
    script_path = os.path.join(base_dir, script)  # Crear la ruta absoluta
    try:
        print(f"Ejecutando: {script_path}")
        result = subprocess.run(["python", script_path], capture_output=True, text=True)

        # Mostrar la salida del script
        print(result.stdout)

        # Verificar errores
        if result.returncode != 0:
            print(f"Error al ejecutar {script}: {result.stderr}")
            break

    except Exception as e:
        print(f"Error inesperado al ejecutar {script}: {e}")
        break

print("Ejecución de scripts completada.")
