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
# ¿este archivo se está ejecutando directamente por el usuario o está siendo importado por otro script?
if __name__ == "__main__":
    # indica dónde está el script actual
    print(f"Ejecutando script desde: {os.path.abspath(__file__)}")
   
    # llama a la función de arriba para cargar el csv
    dataframe_retail = cargar_datos(DATA_PATH)

    if dataframe_retail is not None:
        print("\n---Primeras 5 filas---")
        print(dataframe_retail.head())

        print("\n---Información del DataFrame---")
        dataframe_retail.info(show_counts=True)