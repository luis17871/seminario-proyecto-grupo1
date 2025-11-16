"""
model_saving.py

Modulo para guardar modelos, datos procesados y generar reportes.
Incluye funciones para persistencia de modelos con joblib y generacion de reportes ejecutivos.
"""

import os
import joblib
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from typing import Dict, List


def crear_directorios_salida(directorios: List[str]) -> None:
    """
    Crea los directorios necesarios si no existen.
    
    Parametros:
    -----------
    directorios : List[str]
        Lista de rutas de directorios a crear
    """
    for directorio in directorios:
        os.makedirs(directorio, exist_ok=True)
        print(f"[DIRECTORIO] {directorio} verificado/creado")


def guardar_modelos_clustering(
    kmeans: KMeans,
    scaler: StandardScaler,
    pca: PCA,
    n_clusters: int,
    directorio_modelos: str = 'models'
) -> Dict[str, str]:
    """
    Guarda los modelos entrenados usando joblib.
    
    Parametros:
    -----------
    kmeans : KMeans
        Modelo K-Means entrenado
    scaler : StandardScaler
        Scaler ajustado a los datos
    pca : PCA
        Objeto PCA ajustado
    n_clusters : int
        Numero de clusters del modelo
    directorio_modelos : str
        Directorio donde guardar los modelos (default: 'models')
        
    Retorna:
    --------
    Dict[str, str]
        Diccionario con las rutas de los archivos guardados
    """
    crear_directorios_salida([directorio_modelos])
    
    # Nombres de archivos
    kmeans_path = os.path.join(directorio_modelos, f'kmeans_model_k{n_clusters}.joblib')
    scaler_path = os.path.join(directorio_modelos, f'scaler_kmeans_k{n_clusters}.joblib')
    pca_path = os.path.join(directorio_modelos, f'pca_kmeans_k{n_clusters}.joblib')
    
    # Guardar modelos
    joblib.dump(kmeans, kmeans_path)
    joblib.dump(scaler, scaler_path)
    joblib.dump(pca, pca_path)
    
    print(f"\n[GUARDADO] Modelos guardados exitosamente:")
    print(f"   - K-Means: {kmeans_path}")
    print(f"   - Scaler: {scaler_path}")
    print(f"   - PCA: {pca_path}")
    
    return {
        'kmeans': kmeans_path,
        'scaler': scaler_path,
        'pca': pca_path
    }


def exportar_datos_segmentados(
    df_con_clusters: pd.DataFrame,
    n_clusters: int,
    directorio_datos: str = 'data/processed'
) -> str:
    """
    Exporta los datos con segmentos asignados a CSV.
    
    Parametros:
    -----------
    df_con_clusters : pd.DataFrame
        DataFrame con la columna 'segment'
    n_clusters : int
        Numero de clusters
    directorio_datos : str
        Directorio donde guardar el CSV (default: 'data/processed')
        
    Retorna:
    --------
    str
        Ruta del archivo CSV guardado
    """
    crear_directorios_salida([directorio_datos])
    
    # Nombre del archivo
    csv_path = os.path.join(directorio_datos, f'clientes_mayoristas_segmentados_k{n_clusters}.csv')
    
    # Guardar CSV
    df_con_clusters.to_csv(csv_path, index=False)
    
    print(f"\n[EXPORTACION] Datos segmentados guardados:")
    print(f"   - Archivo: {csv_path}")
    print(f"   - Registros: {len(df_con_clusters)}")
    print(f"   - Columnas: {df_con_clusters.shape[1]}")
    
    return csv_path


def generar_resumen_ejecutivo_csv(
    interpretaciones: Dict[int, Dict[str, str]],
    n_clusters: int,
    directorio_reportes: str = 'data/processed',
    df_con_clusters: pd.DataFrame = None
) -> str:
    """
    Genera un resumen ejecutivo de los clusters en formato CSV.
    
    Parametros:
    -----------
    interpretaciones : Dict[int, Dict[str, str]]
        Diccionario con interpretaciones de cada cluster
    n_clusters : int
        Numero de clusters
    directorio_reportes : str
        Directorio donde guardar el resumen (default: 'data/processed')
    df_con_clusters : pd.DataFrame
        DataFrame con los datos y clusters asignados (opcional, para calcular estadisticas)
        
    Retorna:
    --------
    str
        Ruta del archivo CSV generado
    """
    crear_directorios_salida([directorio_reportes])
    
    # Preparar datos para el resumen
    resumen_data = []
    for cluster_id in sorted(interpretaciones.keys()):
        interp = interpretaciones[cluster_id]
        
        fila = {
            'cluster_id': cluster_id,
            'nombre_segmento': interp.get('nombre_segmento', ''),
            'estrategia_comercial': interp.get('estrategia_comercial', '')
        }
        
        # Si tenemos el dataframe, calcular estadisticas
        if df_con_clusters is not None:
            cluster_data = df_con_clusters[df_con_clusters['segment'] == cluster_id]
            fila['n_clientes'] = len(cluster_data)
            fila['porcentaje_total'] = f"{(len(cluster_data) / len(df_con_clusters)) * 100:.1f}%"
        
        resumen_data.append(fila)
    
    # Crear DataFrame y guardar
    df_resumen = pd.DataFrame(resumen_data)
    
    csv_path = os.path.join(directorio_reportes, f'resumen_ejecutivo_k{n_clusters}.csv')
    
    # Guardar archivo sin timestamp para facilitar el acceso desde la API
    df_resumen.to_csv(csv_path, index=False, encoding='utf-8')
    
    print(f"\n[RESUMEN CSV] Resumen ejecutivo generado:")
    print(f"   - Archivo: {csv_path}")
    print(f"   - Clusters: {len(df_resumen)}")
    
    return csv_path


def generar_acciones_comerciales_por_cluster(
    df_con_clusters: pd.DataFrame,
    interpretaciones: Dict[int, Dict[str, str]],
    n_clusters: int,
    directorio_reportes: str = 'data/processed'
) -> str:
    """
    Genera un archivo CSV con clientes y acciones comerciales recomendadas por cluster.
    
    Parametros:
    -----------
    df_con_clusters : pd.DataFrame
        DataFrame con customer_id y segment
    interpretaciones : Dict[int, Dict[str, str]]
        Diccionario con interpretaciones de cada cluster
    n_clusters : int
        Numero de clusters
    directorio_reportes : str
        Directorio donde guardar el archivo (default: 'data/processed')
        
    Retorna:
    --------
    str
        Ruta del archivo CSV generado
    """
    crear_directorios_salida([directorio_reportes])
    
    # Crear DataFrame con acciones comerciales
    df_acciones = df_con_clusters[['customer_id', 'segment']].copy()
    
    # Agregar informacion del cluster
    df_acciones['nombre_segmento'] = df_acciones['segment'].map(
        {cluster_id: interp['nombre_segmento'] for cluster_id, interp in interpretaciones.items()}
    )
    
    df_acciones['estrategia_comercial'] = df_acciones['segment'].map(
        {cluster_id: interp['estrategia_comercial'] for cluster_id, interp in interpretaciones.items()}
    )
    
    # Guardar archivo sin timestamp para facilitar el acceso
    csv_path = os.path.join(directorio_reportes, f'acciones_comerciales_k{n_clusters}.csv')
    
    df_acciones.to_csv(csv_path, index=False, encoding='utf-8')
    
    print(f"\n[ACCIONES COMERCIALES] Archivo generado:")
    print(f"   - Archivo: {csv_path}")
    print(f"   - Registros: {len(df_acciones)}")
    
    return csv_path