import subprocess
import os

# Definir la lista de scripts en el orden de ejecución
scripts = [
    "Scripts/Stock_actual.py",
    "Scripts/Proyección_demanda.py",
    "Scripts/Modelo_optimización_Stock.py",
    "Scripts/Consolidado_resultados.py"
]

# Ejecutar cada script
for script in scripts:
    try:
        print(f"Ejecutando: {script}")
        result = subprocess.run(["python", script], capture_output=True, text=True)

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
