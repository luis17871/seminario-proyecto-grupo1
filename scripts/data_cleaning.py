import pandas as pd
import numpy as np

def limpieza_nombres_columnas(df):
    """
    toma un df, renombra las columnas específicas y luego
    convierte todos los nombres de la columna en minúsculas
    """
    print("Iniciando limpieza de columnas")
    retail_columnas_renombradas = df.rename(
        columns = {
            "Invoice":"Invoice_Number",
            "StockCode":"Product_Code",
            "Description":"Product_Description",
            "Quantity":"Product_Quantity",
            "InvoiceDate":"Invoice_Date",
            "Price":"Product_Price",
            "Customer ID":"Customer_ID"
            }
        )
    retail_columnas_renombradas.columns = retail_columnas_renombradas.columns.str.lower()

    print("Nombre de columnas limpias")
    return retail_columnas_renombradas


def convertir_customerId_int(df):
    """
    convierte 'customer_id' de float64 a Int64
    """
    print("Convirtiendo 'customer_id' a Int64...")

    df["customer_id"] = df["customer_id"].astype("Int64")

    return df


def limpieza_ausentes_customerId(df):
    """
    elimina filas que no contienen 'customer_id'
    """
    print("Iniciando eliminación de filas con 'customer_id' ausente...")
    filas_antes = len(df)

    df_limpio_customerId = df.dropna(
        subset=['customer_id'],
        how='all')
    df_limpio_customerId = df_limpio_customerId.reset_index(drop=True)

    filas_despues = len(df_limpio_customerId)

    print(f"Filas eliminadas en este paso: {filas_antes - filas_despues}")

    return df_limpio_customerId


def normalizar_product_description(df):
    """
    convierte a minúsculas y elimina espacios en blanco
    en 'product_description'
    """
    print("Normalizando 'product_description'...")

    df["product_description"] = df["product_description"].str.lower().str.strip()

    return df


def limpiar_cancelaciones(df):
    """
    elimina filas correspondientes a cancelaciones
    (cantidad negativa)
    """
    print("Eliminando filas correspondientes a cancelaciones...")

    filas_antes = len(df)

    facturas_con_devoluciones = df[df['product_quantity'] < 0]['invoice_number'].unique()

    df_limpio = df[~df['invoice_number'].isin(facturas_con_devoluciones)].reset_index(drop=True)

    filas_despues = len(df_limpio)

    print(f"Filas eliminadas en este paso: {filas_antes - filas_despues}")

    return df_limpio


def limpiar_product_price_negativos_o_cero(df):
    """
    elimina filas con 'product_price' negativos o cero
    """
    print("Eliminando filas con 'product_price' negativos o cero...")

    filas_antes = len(df)

    df_limpio = df[df['product_price'] > 0].reset_index(drop=True)

    filas_despues = len(df_limpio)

    print(f"Filas eliminadas en este paso: {filas_antes - filas_despues}")

    return df_limpio


def reemplazar_EIRE(df):
    """
    reemplaza 'EIRE' por 'IRELAND' en la columna 'country'
    """
    print("Reemplazando 'EIRE' por 'IRELAND' en la columna 'country'...")

    df['country'] = df['country'].replace('EIRE', 'IRELAND')

    return df

def limpiar_datos(df):
    """
    Ejecuta la secuencia completa de limpieza llamando
    a las funciones existentes en orden lógico.
    """
    print("\n[INFO] Iniciando limpieza general de datos...")

    df = limpieza_nombres_columnas(df)
    df = convertir_customerId_int(df)
    df = limpieza_ausentes_customerId(df)
    df = normalizar_product_description(df)
    df = limpiar_cancelaciones(df)
    df = limpiar_product_price_negativos_o_cero(df)
    df = reemplazar_EIRE(df)

    print("[OK] Limpieza completada correctamente.\n")
    return df
