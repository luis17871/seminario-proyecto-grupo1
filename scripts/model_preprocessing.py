"""
model_preprocessing.py

Modulo para el preprocesamiento de datos para clustering K-Means.
Incluye funciones para preparacion de features, normalizacion y analisis del numero optimo de clusters.
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
from typing import Tuple, Dict, List


def preparar_features_clustering(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Prepara las features para clustering eliminando identificadores.
    
    Parametros:
    -----------
    df : pd.DataFrame
        DataFrame con los datos originales incluyendo customer_id
        
    Retorna:
    --------
    Tuple[pd.DataFrame, pd.Series]
        - features_for_clustering: DataFrame con solo las features numericas
        - customer_ids: Series con los IDs de clientes para referencia posterior
    """
    # Guardar customer_id para despues
    customer_ids = df['customer_id'].copy() if 'customer_id' in df.columns else df.index.copy()
    
    # Preparar features para clustering (eliminar identificadores)
    features_for_clustering = df.drop('customer_id', axis=1) if 'customer_id' in df.columns else df.copy()
    
    print("[PREPROCESSING] Features preparadas para clustering")
    print(f"   - Columnas: {features_for_clustering.columns.tolist()}")
    print(f"   - Shape: {features_for_clustering.shape}")
    
    return features_for_clustering, customer_ids


def normalizar_features(features: pd.DataFrame) -> Tuple[np.ndarray, StandardScaler, pd.DataFrame]:
    """
    Normaliza las features usando StandardScaler.
    
    Parametros:
    -----------
    features : pd.DataFrame
        DataFrame con las features a normalizar
        
    Retorna:
    --------
    Tuple[np.ndarray, StandardScaler, pd.DataFrame]
        - features_scaled: Array numpy con features normalizadas
        - scaler: Objeto StandardScaler ajustado (para transformar datos nuevos)
        - features_scaled_df: DataFrame con features normalizadas (para analisis)
    """
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)
    
    # Convertir a DataFrame para mantener nombres de columnas
    features_scaled_df = pd.DataFrame(
        features_scaled,
        columns=features.columns,
        index=features.index
    )
    
    print("[PREPROCESSING] Datos normalizados con StandardScaler")
    print(f"   - Media de features escaladas: {features_scaled.mean(axis=0).round(4)}")
    print(f"   - Desviacion estandar: {features_scaled.std(axis=0).round(4)}")
    
    return features_scaled, scaler, features_scaled_df


def analizar_numero_optimo_clusters(
    features_scaled: np.ndarray,
    k_min: int = 2,
    k_max: int = 11,
    random_state: int = 42
) -> Dict[str, any]:
    """
    Analiza el numero optimo de clusters usando Elbow Method y Silhouette Score.
    
    Parametros:
    -----------
    features_scaled : np.ndarray
        Features normalizadas para clustering
    k_min : int
        Numero minimo de clusters a evaluar (default: 2)
    k_max : int
        Numero maximo de clusters a evaluar (default: 11)
    random_state : int
        Semilla para reproducibilidad (default: 42)
        
    Retorna:
    --------
    Dict[str, any]
        Diccionario con los resultados del analisis:
        - 'k_range': Rango de valores k evaluados
        - 'wcss': Lista de valores WCSS (Within-Cluster Sum of Squares)
        - 'silhouette_scores': Lista de Silhouette Scores
        - 'optimal_k_silhouette': k optimo segun Silhouette Score
        - 'max_silhouette_score': Valor maximo de Silhouette Score
    """
    wcss = []
    silhouette_scores = []
    K_range = range(k_min, k_max)
    
    print(f"\n[ANALISIS] Evaluando numero optimo de clusters (k={k_min} a k={k_max-1})")
    print("="*80)
    
    for k in K_range:
        kmeans = KMeans(n_clusters=k, random_state=random_state, n_init=10)
        kmeans.fit(features_scaled)
        
        wcss_value = kmeans.inertia_
        silhouette = silhouette_score(features_scaled, kmeans.labels_)
        
        wcss.append(wcss_value)
        silhouette_scores.append(silhouette)
        
        print(f"K={k}: WCSS={wcss_value:.2f}, Silhouette Score={silhouette:.4f}")
    
    # Encontrar k optimo segun Silhouette Score
    optimal_k_idx = np.argmax(silhouette_scores)
    optimal_k = K_range[optimal_k_idx]
    max_silhouette = silhouette_scores[optimal_k_idx]
    
    print("="*80)
    print(f"[RECOMENDACION] K optimo segun Silhouette Score: k={optimal_k}")
    print(f"                 Silhouette Score maximo: {max_silhouette:.4f}")
    print("="*80)
    
    return {
        'k_range': list(K_range),
        'wcss': wcss,
        'silhouette_scores': silhouette_scores,
        'optimal_k_silhouette': optimal_k,
        'max_silhouette_score': max_silhouette
    }


def crear_pca_visualizacion(features_scaled: np.ndarray, n_components: int = 2) -> Tuple[PCA, np.ndarray]:
    """
    Crea un objeto PCA para visualizacion en 2D.
    
    Parametros:
    -----------
    features_scaled : np.ndarray
        Features normalizadas
    n_components : int
        Numero de componentes principales (default: 2 para visualizacion 2D)
        
    Retorna:
    --------
    Tuple[PCA, np.ndarray]
        - pca: Objeto PCA ajustado
        - features_pca: Features transformadas a n_components dimensiones
    """
    pca = PCA(n_components=n_components)
    features_pca = pca.fit_transform(features_scaled)
    
    varianza_explicada = sum(pca.explained_variance_ratio_) * 100
    
    print(f"\n[PCA] Reduccion dimensional a {n_components} componentes")
    print(f"   - Varianza explicada: {varianza_explicada:.2f}%")
    print(f"   - Varianza por componente: {[f'{v*100:.2f}%' for v in pca.explained_variance_ratio_]}")
    
    return pca, features_pca