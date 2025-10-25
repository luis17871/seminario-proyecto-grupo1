import pandas as pd
import numpy as np
from datetime import datetime


def calcular_rfm(df: pd.DataFrame, fecha_corte: datetime | None = None) -> pd.DataFrame:
    """
    Calcula las métricas Recency (R), Frequency (F) y Monetary (M) para cada cliente.

    Parámetros:
        df (pd.DataFrame): DataFrame limpio con columnas de ventas.
        fecha_corte (datetime, opcional): Fecha de referencia para calcular la recencia.
                                          Si no se proporciona, se usa la fecha máxima del dataset.

    Retorna:
        pd.DataFrame: DataFrame con las columnas R, F, M por cliente.
    """
    df = df.copy()

    # Detectar columnas de cantidad y precio
    
    if "product_quantity" in df.columns and "product_price" in df.columns:
        cantidad_col = "product_quantity"
        precio_col = "product_price"
    elif "Quantity" in df.columns and "Price" in df.columns:
        cantidad_col = "Quantity"
        precio_col = "Price"
    else:
        raise KeyError(
            "No se encontraron columnas de cantidad y precio. "
            "Verifica que el DataFrame tenga 'product_quantity' y 'product_price' "
            "o las originales 'Quantity' y 'Price'."
        )

    # Calcular el total de cada transacción
    df["total"] = df[cantidad_col] * df[precio_col]

    # Detectar columnas de fecha, cliente e invoice

    if "invoice_date" in df.columns:
        fecha_col = "invoice_date"
    else:
        fecha_col = "InvoiceDate"

    if "customer_id" in df.columns:
        cliente_col = "customer_id"
    else:
        cliente_col = "Customer ID"

    if "invoice_number" in df.columns:
        factura_col = "invoice_number"
    else:
        factura_col = "Invoice"

    # Convertir columna de fecha a datetime
    df[fecha_col] = pd.to_datetime(df[fecha_col], errors="coerce")

    # Eliminar registros sin fecha válida
    df = df.dropna(subset=[fecha_col])

    # Determinar fecha de corte
    if fecha_corte is None:
        fecha_corte = df[fecha_col].max()
    
    # Agrupar por cliente y calcular métricas RFM
    agg = {
        fecha_col: lambda s: (fecha_corte - s.max()).days,
        factura_col: pd.Series.nunique,
        "total": "sum"
    }

    rfm = df.groupby(cliente_col).agg(agg).reset_index()
    rfm.columns = ["cliente_id", "R", "F", "M"]
    rfm["R"] = rfm["R"].clip(lower=0)

    return rfm


def cuantiles_rfm(rfm: pd.DataFrame) -> pd.DataFrame:
    """
    Asigna puntajes de 1 a 4 a las métricas R, F, M según cuantiles.

    Retorna:
        DataFrame con columnas R_score, F_score, M_score, RFM_score_sum y RFM_score_str.
    """
    def qcut_safe(series, q=4, reverse=False):
        if series.nunique() == 1:
            return pd.Series([2] * len(series), index=series.index)
        scored = pd.qcut(series.rank(method="first"), q=q, labels=[1, 2, 3, 4], duplicates="drop")
        if reverse:
            inv_map = {1: 4, 2: 3, 3: 2, 4: 1}
            return scored.astype(int).map(inv_map)
        return scored.astype(int)

    rfm["R_score"] = qcut_safe(rfm["R"], reverse=True)
    rfm["F_score"] = qcut_safe(rfm["F"])
    rfm["M_score"] = qcut_safe(rfm["M"])
    rfm["RFM_score_sum"] = rfm[["R_score", "F_score", "M_score"]].sum(axis=1)
    rfm["RFM_score_str"] = (
        rfm["R_score"].astype(str)
        + rfm["F_score"].astype(str)
        + rfm["M_score"].astype(str)
    )
    return rfm


def reglas_negocio_segmento(r, f, m, rfm_sum):
    """
    Clasifica a cada cliente en un segmento según su puntaje RFM.
    """
    if rfm_sum >= 10 and (f >= 3 and m >= 3):
        return "VIP"
    elif f >= 3 and m >= 2 and r >= 2:
        return "Leal"
    elif r <= 2 and m <= 2:
        return "En_Riesgo"
    elif f == 1 and m == 1 and r <= 2:
        return "Durmiente"
    else:
        return "Prometedor"


def asignar_segmentos(rfm: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica las reglas de negocio y añade la columna 'segmento_final'.
    """
    rfm["segmento_final"] = rfm.apply(
        lambda x: reglas_negocio_segmento(
            r=x["R_score"],
            f=x["F_score"],
            m=x["M_score"],
            rfm_sum=x["RFM_score_sum"]
        ),
        axis=1
    )
    return rfm


def generar_features_rfm(df: pd.DataFrame) -> pd.DataFrame:
    """
    Función principal del módulo.
    Toma un DataFrame limpio, calcula RFM y devuelve los resultados con segmentación.
    """
    print("[INFO] Generando métricas RFM y segmentos...")
    rfm = calcular_rfm(df)
    rfm = cuantiles_rfm(rfm)
    rfm = asignar_segmentos(rfm)
    print("[OK] Features RFM generadas correctamente ✅")
    return rfm
