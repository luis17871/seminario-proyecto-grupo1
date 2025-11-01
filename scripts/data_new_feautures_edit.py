import pandas as pd
import datetime as dt
import numpy as np
import matplotlib.pyplot as plt
import os

def normalizar_fechas(df):
    """
    Normaliza la columna 'invoice_date' a formato datetime.
    """
    print("Normalizando fechas en 'invoice_date'...")

    df['invoice_date'] = pd.to_datetime(df['invoice_date'])
    return df

def calcular_recency(df):
    """
    Calcula la recencia de las compras por cliente.
    """
    print("Calculando recencia...")
    db_recency = df.groupby(by='customer_id', as_index=False)['invoice_date'].max()
    db_recency.columns = ['customer_id', 'last_purchase_date']
    recent_date = db_recency['last_purchase_date'].max()
    db_recency['recency'] = db_recency['last_purchase_date'].apply(lambda x: (recent_date - x).days)
    return db_recency

def calcular_frecuency(df):
    """
    Calcula la frecuencia de compras por cliente.
    """
    print("Calculando frecuencia...")
    db_frecuency = df.drop_duplicates(subset=['invoice_number', 'product_code', 'customer_id']).groupby(by='customer_id', as_index=False)['invoice_date'].count()
    db_frecuency.columns = ['customer_id', 'frequency']
    return db_frecuency

def calcular_monetary(df):
    """
    Calcula el valor monetario de las compras por cliente.
    """
    print("Calculando valor monetario...")
    df['TotalSum'] = df['product_price'] * df['product_quantity']
    df['TotalSum'] = df['TotalSum'].round(2)
    db_monetary = df.groupby(by="customer_id", as_index=False)['TotalSum'].sum()
    db_monetary.columns = ['customer_id', 'monetary']
    return db_monetary

def construir_rfm(db_recency, db_frecuency, db_monetary):
    """
    Construye el dataframe RFM a partir de las tablas de recencia, frecuencia y valor monetario.
    """
    print("Construyendo dataframe RFM...")
    # unir las 3 df
    df_rf = db_recency.merge(db_frecuency, on = 'customer_id')
    df_rfm = df_rf.merge(db_monetary, on = 'customer_id').drop(columns=['last_purchase_date'])
    # rankear R, F, M
    df_rfm['R_rank'] = df_rfm['recency'].rank(ascending=False)
    df_rfm['F_rank'] = df_rfm['frequency'].rank(ascending=True)
    df_rfm['M_rank'] = df_rfm['monetary'].rank(ascending=True)
    # Normalizando los ranks
    df_rfm['R_rank_norm'] = (df_rfm['R_rank'] / df_rfm['R_rank'].max()) * 100
    df_rfm['F_rank_norm'] = (df_rfm['F_rank'] / df_rfm['F_rank'].max()) * 100
    df_rfm['M_rank_norm'] = (df_rfm['M_rank'] / df_rfm['M_rank'].max()) * 100
    # Dropear los ranks individuales
    df_rfm.drop(columns=['R_rank', 'F_rank', 'M_rank'], inplace=True)
    # Calcular el RFM Score ponderado
    # Asignación de pesos ponderados y cálculo del RFM Score
    df_rfm['RFM_Score'] = 0.15 * df_rfm['R_rank_norm'] + 0.28 * df_rfm['F_rank_norm'] + 0.57 * df_rfm['M_rank_norm']
    # Asignación de escala de 0 a 5 para reducir el rango del RFM Score y su mejora en la segmentación
    df_rfm['RFM_Score'] *= 0.05
    
    # Redondear a 2 decimales los campos normalizados y el score final
    df_rfm['R_rank_norm'] = df_rfm['R_rank_norm'].round(2)
    df_rfm['F_rank_norm'] = df_rfm['F_rank_norm'].round(2)
    df_rfm['M_rank_norm'] = df_rfm['M_rank_norm'].round(2)
    df_rfm['RFM_Score'] = df_rfm['RFM_Score'].round(2)
    df_rfm['monetary'] = df_rfm['monetary'].round(2)
    
    return df_rfm

def generar_indicadores_rfm(df: pd.DataFrame) -> pd.DataFrame:
    """
    Función principal del módulo.
    Toma un DataFrame limpio, genera las métricas RFM y devuelve el DataFrame con las nuevas características.
    """
    print("[INFO] Generando métricas RFM y segmentos...")
    nf = normalizar_fechas(df)
    rdm = calcular_recency(nf)
    rfq = calcular_frecuency(nf)
    rfm = calcular_monetary(nf)
    rfm = construir_rfm(rdm, rfq, rfm)
    print("[OK] Features RFM generadas correctamente")
    return rfm