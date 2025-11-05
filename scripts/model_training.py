"""
model_training.py

Modulo para el entrenamiento de modelos K-Means y analisis de clusters.
Incluye funciones para entrenar el modelo, asignar clusters e interpretar segmentos mayoristas.
"""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score
from typing import Tuple, Dict, List, Any


def entrenar_kmeans(
    features_scaled: np.ndarray,
    n_clusters: int = 3,
    random_state: int = 42,
    n_init: int = 10,
    max_iter: int = 300
) -> Tuple[KMeans, Dict[str, float]]:
    """
    Entrena un modelo K-Means con los parametros especificados.
    
    Parametros:
    -----------
    features_scaled : np.ndarray
        Features normalizadas para clustering
    n_clusters : int
        Numero de clusters (default: 3)
    random_state : int
        Semilla para reproducibilidad (default: 42)
    n_init : int
        Numero de inicializaciones diferentes (default: 10)
    max_iter : int
        Maximo numero de iteraciones (default: 300)
        
    Retorna:
    --------
    Tuple[KMeans, Dict[str, float]]
        - kmeans: Modelo K-Means entrenado
        - metricas: Diccionario con metricas de evaluacion
    """
    print(f"\n[TRAINING] Entrenando K-Means con k={n_clusters}")
    print("="*80)
    
    # Entrenar modelo
    kmeans = KMeans(
        n_clusters=n_clusters,
        random_state=random_state,
        n_init=n_init,
        max_iter=max_iter
    )
    kmeans.fit(features_scaled)
    
    # Calcular metricas de evaluacion
    labels = kmeans.labels_
    silhouette = silhouette_score(features_scaled, labels)
    davies_bouldin = davies_bouldin_score(features_scaled, labels)
    calinski_harabasz = calinski_harabasz_score(features_scaled, labels)
    inertia = kmeans.inertia_
    
    metricas = {
        'silhouette_score': silhouette,
        'davies_bouldin_score': davies_bouldin,
        'calinski_harabasz_score': calinski_harabasz,
        'inertia': inertia,
        'n_clusters': n_clusters,
        'n_iter': kmeans.n_iter_
    }
    
    print(f"[METRICAS] Modelo entrenado exitosamente")
    print(f"   - Silhouette Score: {silhouette:.4f} (mas cercano a 1 es mejor)")
    print(f"   - Davies-Bouldin Index: {davies_bouldin:.4f} (mas cercano a 0 es mejor)")
    print(f"   - Calinski-Harabasz Score: {calinski_harabasz:.2f} (mayor es mejor)")
    print(f"   - Inertia (WCSS): {inertia:.2f}")
    print(f"   - Iteraciones hasta convergencia: {kmeans.n_iter_}")
    print("="*80)
    
    return kmeans, metricas


def asignar_clusters_a_dataframe(
    df_original: pd.DataFrame,
    labels: np.ndarray,
    nombre_columna: str = 'segment'
) -> pd.DataFrame:
    """
    Asigna las etiquetas de cluster al DataFrame original.
    
    Parametros:
    -----------
    df_original : pd.DataFrame
        DataFrame original con los datos
    labels : np.ndarray
        Etiquetas de cluster asignadas por K-Means
    nombre_columna : str
        Nombre de la columna para los clusters (default: 'segment')
        
    Retorna:
    --------
    pd.DataFrame
        DataFrame con la columna de segmentos anadida
    """
    df_con_clusters = df_original.copy()
    df_con_clusters[nombre_columna] = labels
    
    # Mostrar distribucion de clusters
    distribucion = df_con_clusters[nombre_columna].value_counts().sort_index()
    
    print(f"\n[ASIGNACION] Clusters asignados en columna '{nombre_columna}'")
    print(f"   - Total de registros: {len(df_con_clusters)}")
    print(f"\n   Distribucion de clusters:")
    for cluster, count in distribucion.items():
        porcentaje = (count / len(df_con_clusters)) * 100
        print(f"      Cluster {cluster}: {count} clientes ({porcentaje:.1f}%)")
    
    return df_con_clusters


def generar_interpretaciones_todos_clusters(
    df_con_clusters: pd.DataFrame,
    feature_names: List[str],
    n_clusters: int
) -> Dict[int, Dict[str, str]]:
    """
    Genera interpretaciones para todos los clusters usando RANKING por RFM Score.
    FUNCION EXACTA DEL NOTEBOOK.
    
    Parametros:
    -----------
    df_con_clusters : pd.DataFrame
        DataFrame con la columna 'segment' asignada
    feature_names : List[str]
        Lista de nombres de features utilizadas (debe incluir 'RFM_Score')
    n_clusters : int
        Numero total de clusters
        
    Retorna:
    --------
    Dict[int, Dict[str, str]]
        Diccionario con interpretaciones de cada cluster con keys:
        - 'nombre_segmento': Nombre del segmento
        - 'estrategia_comercial': Estrategia comercial recomendada
    """
    # Calcular distribucion de clusters
    distribution = df_con_clusters['segment'].value_counts().sort_index()
    
    # Calcular perfil de cada cluster (mean, median, etc.)
    cluster_profile = df_con_clusters.groupby('segment')[feature_names].agg(['mean', 'median', 'std', 'min', 'max'])
    
    # PASO 1: Obtener todos los RFM Scores promedio de cada cluster
    rfm_scores_por_cluster = {}
    for cluster_id in sorted(distribution.index):
        profile_mean = cluster_profile.xs('mean', level=1, axis=1).loc[cluster_id]
        rfm_scores_por_cluster[cluster_id] = profile_mean.get('RFM_Score', 0)
    
    # PASO 2: Ordenar clusters por RFM Score de mayor a menor
    clusters_ordenados = sorted(rfm_scores_por_cluster.items(), key=lambda x: x[1], reverse=True)
    print("\n[RANKING] Clusters ordenados por RFM Score (de mayor a menor):")
    for cluster_id, score in clusters_ordenados:
        print(f"  Cluster {cluster_id}: RFM Score = {score:.2f}")
    
    # PASO 3: Asignar segmentos basados en POSICION en el ranking
    interpretaciones = {}
    
    for posicion, (cluster_id, score) in enumerate(clusters_ordenados, 1):
        profile_mean = cluster_profile.xs('mean', level=1, axis=1).loc[cluster_id]
        
        # Determinar categoria segun posicion
        if n_clusters == 3:
            if posicion == 1:
                nombre_segmento = 'Clientes VIP'
                estrategia = 'Gerente de cuenta dedicado, condiciones comerciales premium y precios especiales, acceso prioritario a nuevos productos, programas de fidelizacion exclusivos'
            elif posicion == 2:
                nombre_segmento = 'Clientes Leales'
                estrategia = 'Programa de fidelizacion con beneficios progresivos, descuentos por volumen y promociones exclusivas, cross-selling de productos complementarios, invitacion a programa VIP'
            else:  # posicion == 3
                nombre_segmento = 'Clientes en riesgo'
                estrategia = 'Contacto directo para identificar problemas, descuentos agresivos de recuperacion, ofertas "ultima oportunidad", mejora de condiciones comerciales, visitas comerciales'
        
        elif n_clusters == 2:
            if posicion == 1:
                nombre_segmento = 'Clientes VIP'
                estrategia = 'Retencion y maximizacion, programas premium, fidelizacion'
            else:
                nombre_segmento = 'Clientes en riesgo'
                estrategia = 'Reactivacion urgente, ofertas especiales, seguimiento'
        
        elif n_clusters == 4:
            if posicion == 1:
                nombre_segmento = 'Clientes VIP'
                estrategia = 'Retencion y maximizacion premium'
            elif posicion == 2:
                nombre_segmento = 'Clientes Leales'
                estrategia = 'Desarrollo y upselling'
            elif posicion == 3:
                nombre_segmento = 'Clientes Regulares'
                estrategia = 'Activacion y engagement'
            else:
                nombre_segmento = 'Clientes en riesgo'
                estrategia = 'Reactivacion urgente'
        
        else:  # 5+ clusters
            proporcion = posicion / n_clusters
            if proporcion <= 0.20:
                nombre_segmento = 'Clientes VIP'
                estrategia = 'Maxima prioridad, retencion premium'
            elif proporcion <= 0.40:
                nombre_segmento = 'Clientes Leales'
                estrategia = 'Desarrollo y crecimiento'
            elif proporcion <= 0.70:
                nombre_segmento = 'Clientes Regulares'
                estrategia = 'Activacion y mejora'
            else:
                nombre_segmento = 'Clientes en riesgo'
                estrategia = 'Reactivacion y recuperacion'
        
        interpretaciones[cluster_id] = {
            'nombre_segmento': nombre_segmento,
            'estrategia_comercial': estrategia
        }
        
        # Mostrar info
        count = distribution[cluster_id]
        percentage = (count / len(df_con_clusters)) * 100
        print(f"\n{'-'*80}")
        print(f"CLUSTER {cluster_id}: {nombre_segmento.upper()}")
        print(f"Ranking: #{posicion} de {n_clusters} (RFM Score: {score:.2f})")
        print(f"Clientes: {count:,} ({percentage:.2f}%)")
        print(f"Estrategia: {estrategia}")
        print(f"Recency: {profile_mean.get('recency', 0):.2f} | Frequency: {profile_mean.get('frequency', 0):.2f} | Monetary: ${profile_mean.get('monetary', 0):,.2f}")
    
    print("="*80)
    print("[OK] INTERPRETACION COMPLETADA")
    print("="*80)
    
    return interpretaciones
