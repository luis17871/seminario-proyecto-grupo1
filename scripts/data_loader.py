import pandas as pd
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_PATH = os.path.join(SCRIPT_DIR, "..", "data", "BASERETAIL.csv")

def cargar_datos(path):
    print(f"Cargando datos desde {path}...")
    try:
        df = pd.read_csv(path)
        print("Datos cargados exitosamente.")
        return df
    except FileNotFoundError:
        print(f"Error: El archivo en la ruta {path} no fue encontrado.")
        print("Asegúrate de tener el archivo en la carpeta 'data'.")
        return None
    except Exception as e:
        print(f"Ocurrió un error inesperado al cargar los datos: {e}")
        return None