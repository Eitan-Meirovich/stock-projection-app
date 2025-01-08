import subprocess
import os

# Obtener el directorio base (donde se encuentra Main.py)
base_dir = r'C:\Users\Ukryl\stock-projection-app\demand_forecasting_project'

# Definir la lista de scripts en el orden de ejecución con rutas absolutas
scripts = [
    "run_processor.py",
    "src/data/Data_groups.py",
    "src/models/Invierno/Holt_Sarima25.py",
    "src/models/Invierno/Top_Down.py",
    "src/models/Hilos_Verano/Proyección_Verano.py",
    "src/models/Hilos_Verano/Top_Down_Verano_25.py",
    "src/models/Bebé/Proyecciones_25.py",
    "src/models/Bebé/Top_Down_25.py",
    "Consolidado_resultados.py",
    "merged_data.py"
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
