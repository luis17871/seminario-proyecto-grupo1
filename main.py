import os
from scripts.data_loader import cargar_datos
from scripts.data_cleaning import (
    limpieza_nombres_columnas,
    convertir_customerId_int,
    limpieza_ausentes_customerId,
    normalizar_product_description,
    limpiar_cancelaciones,
    reemplazar_EIRE
    )

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(SCRIPT_DIR, "data", "BASERETAIL.csv")

# este archivo se está ejecutando directamente por el usuario o está siendo importado por otro script?
if __name__ == "__main__":
    # indica dónde está el script actual
    print(f"Ejecutando script desde: {os.path.abspath(__file__)}")

    # llama a la función de arriba para cargar el csv
    dataframe_retail = cargar_datos(DATA_PATH)

    if dataframe_retail is not None:
        # Módulo de limpieza de datos
        print("\n---Iniciando Limpieza de datos---")

        df_limpio = limpieza_nombres_columnas(dataframe_retail)
        df_limpio = convertir_customerId_int(df_limpio)
        df_limpio = limpieza_ausentes_customerId(df_limpio)
        df_limpio = normalizar_product_description(df_limpio)
        df_limpio = limpiar_cancelaciones(df_limpio)
        df_limpio = reemplazar_EIRE(df_limpio)

        print("\n---Finalizando Limpieza de datos---")

        print("\n---Primeras 5 filas---")
        print(df_limpio.head())

        print("\n---Información del DataFrame---")
        df_limpio.info(show_counts=True)
    else:
        print("No se pudo cargar el DataFrame. Terminando el programa.")