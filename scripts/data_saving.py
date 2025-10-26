"""
MÓDULO: data_saving
-------------------------------------
Responsabilidad:
    - Guardar los DataFrames procesados en rutas específicas.
    - Verificar que la carpeta de destino exista.
    - Manejar errores de guardado de manera segura.
"""

import os
import pandas as pd


def guardar_datos_limpios(df: pd.DataFrame, path: str) -> bool:
    """
    Guarda el DataFrame final procesado en un archivo CSV.

    Parámetros:
        df (pd.DataFrame): Datos procesados a guardar.
        path (str): Ruta completa donde se guardará el archivo.

    Retorna:
        bool: True si el guardado fue exitoso, False si hubo error.
    """
    try:
        print("\n[INFO] Guardando datos procesados...")

        # Crear carpeta si no existe
        os.makedirs(os.path.dirname(path), exist_ok=True)

        # Guardar como CSV
        df.to_csv(path, index=False, encoding="utf-8-sig")

        print(f"[OK] Archivo guardado correctamente en:\n{path}")
        return True

    except Exception as e:
        print(f"[ERROR] No se pudo guardar el archivo: {e}")
        return False
