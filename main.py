"""
Archivo principal del pipeline de procesamiento de datos del proyecto:
"Plataforma tecnológica financiera de factoring y confirming: liquidez para PYMES y emprendedores en Ecuador"
"""

# Importación de módulos

from scripts.data_loader import cargar_datos
from scripts.data_cleaning import limpiar_datos
from scripts.imputation import imputar_datos
from scripts.data_new_features import generar_features_rfm
from scripts.data_saving import guardar_datos_limpios
import os

# Función principal

def main():
    print("\n==============================")
    print(" INICIO DEL PIPELINE PRINCIPAL")
    print("==============================\n")

    # Cargar datos
    ruta_datos = os.path.join("data", "BASERETAIL.csv")
    print(f"[1/5] Cargando datos desde: {ruta_datos}")
    df = cargar_datos(ruta_datos)

    if df is None or df.empty:
        print("❌ No se pudieron cargar los datos. Revisa la ruta o el archivo.")
        return

    # Limpieza de datos
    print("[2/5] Aplicando limpieza...")
    df_limpio = limpiar_datos(df)

    # Imputación de valores faltantes
    print("[3/5] Imputando valores faltantes...")
    df_imputado = imputar_datos(df_limpio)

    # Generación de características RFM
    print("[4/5] Generando nuevas características (RFM)...")
    df_features = generar_features_rfm(df_imputado)

    # Guardado final de resultados
    ruta_salida = os.path.join("data", "processed", "clientes_features.csv")
    print("[5/5] Guardando resultados finales...")
    guardar_datos_limpios(df_features, ruta_salida)

    print("\n==============================")
    print(" PIPELINE COMPLETADO CON ÉXITO ✅")
    print("==============================\n")

# Ejecución directa

if __name__ == "__main__":
    main()
