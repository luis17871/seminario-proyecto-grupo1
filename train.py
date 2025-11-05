"""
train.py

Script principal para el entrenamiento del modelo de segmentacion K-Means.
Orquesta todo el pipeline: preprocesamiento, analisis, entrenamiento y guardado.
"""

import sys
import os
import pandas as pd
import argparse
from datetime import datetime

# Agregar el directorio scripts al path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts')
DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "metricas_clientes_ml.csv")
sys.path.insert(0, SCRIPTS_DIR)

# Importar modulos propios
from scripts.model_preprocessing import (
    preparar_features_clustering,
    normalizar_features,
    analizar_numero_optimo_clusters,
    crear_pca_visualizacion
)
from scripts.model_training import (
    entrenar_kmeans,
    asignar_clusters_a_dataframe,
    generar_interpretaciones_todos_clusters
)
from scripts.model_saving import (
    guardar_modelos_clustering,
    exportar_datos_segmentados,
    generar_resumen_ejecutivo_csv,
    generar_acciones_comerciales_por_cluster
)


# CONFIGURACION GLOBAL
RANDOM_STATE = 42
N_INIT = 10
MAX_ITER = 300
K_MIN = 2
K_MAX = 11


def cargar_datos(DATA_PATH: str) -> pd.DataFrame:
    """
    Carga los datos desde un archivo CSV.
    
    Parametros:
    -----------
    ruta_archivo : str
        Ruta al archivo CSV con los datos
        
    Retorna:
    --------
    pd.DataFrame
        DataFrame con los datos cargados
    """
    print("\n" + "="*100)
    print("INICIO DEL PIPELINE DE SEGMENTACION K-MEANS")
    print("="*100)
    print(f"\n[CARGA] Cargando datos desde: {DATA_PATH}")
    
    try:
        df = pd.read_csv(DATA_PATH)
        print(f"[OK] Datos cargados exitosamente")
        print(f"   - Registros: {len(df)}")
        print(f"   - Columnas: {list(df.columns)}")
        print(f"   - Shape: {df.shape}")
        return df
    except Exception as e:
        print(f"[ERROR] No se pudieron cargar los datos: {e}")
        sys.exit(1)


def ejecutar_pipeline_completo(
    DATA_PATH: str,
    n_clusters: int = None,
    analizar_k_optimo: bool = True,
    directorio_modelos: str = 'models',
    directorio_datos: str = 'data/processed'
):
    """
    Ejecuta el pipeline completo de segmentacion K-Means.
    
    Parametros:
    -----------
    ruta_datos : str
        Ruta al archivo CSV con los datos
    n_clusters : int
        Numero de clusters (si None, se usa el analisis automatico)
    analizar_k_optimo : bool
        Si True, realiza analisis de k optimo (default: True)
    directorio_modelos : str
        Directorio para guardar modelos (default: 'models')
    directorio_datos : str
        Directorio para guardar datos procesados (default: 'data/processed')
    """
    inicio_pipeline = datetime.now()
    
    # 1. CARGA DE DATOS
    df = cargar_datos(DATA_PATH)
    
    # 2. PREPROCESAMIENTO
    print("\n" + "="*100)
    print("FASE 1: PREPROCESAMIENTO DE DATOS")
    print("="*100)
    
    features_df, customer_ids = preparar_features_clustering(df)
    features_scaled, scaler, features_scaled_df = normalizar_features(features_df)
    
    # Guardar nombres de features para interpretacion
    feature_names = features_df.columns.tolist()
    print(f"\n[FEATURES] Features seleccionadas: {feature_names}")
    
    # 3. ANALISIS DE K OPTIMO (opcional)
    if analizar_k_optimo:
        print("\n" + "="*100)
        print("FASE 2: ANALISIS DE NUMERO OPTIMO DE CLUSTERS")
        print("="*100)
        
        analisis_k = analizar_numero_optimo_clusters(
            features_scaled,
            k_min=K_MIN,
            k_max=K_MAX,
            random_state=RANDOM_STATE
        )
        
        # Si no se especifico k, usar el optimo del analisis
        if n_clusters is None:
            n_clusters = analisis_k['optimal_k_silhouette']
            print(f"\n[DECISION] Usando k optimo del analisis: k={n_clusters}")
    else:
        if n_clusters is None:
            n_clusters = 3  # Valor por defecto
            print(f"\n[DECISION] Usando k por defecto: k={n_clusters}")
    
    # 4. ENTRENAMIENTO DEL MODELO
    print("\n" + "="*100)
    print("FASE 3: ENTRENAMIENTO DEL MODELO K-MEANS")
    print("="*100)
    
    kmeans, metricas = entrenar_kmeans(
        features_scaled,
        n_clusters=n_clusters,
        random_state=RANDOM_STATE,
        n_init=N_INIT,
        max_iter=MAX_ITER
    )
    
    # 5. ASIGNACION DE CLUSTERS
    print("\n" + "="*100)
    print("FASE 4: ASIGNACION DE CLUSTERS")
    print("="*100)
    
    # Crear DataFrame con customer_id y features originales
    df_completo = df.copy()
    df_con_clusters = asignar_clusters_a_dataframe(
        df_completo,
        kmeans.labels_,
        nombre_columna='segment'
    )
    
    # 6. INTERPRETACION DE CLUSTERS
    print("\n" + "="*100)
    print("FASE 5: INTERPRETACION DE SEGMENTOS")
    print("="*100)
    
    interpretaciones = generar_interpretaciones_todos_clusters(
        df_con_clusters,
        feature_names,
        n_clusters
    )
    
    # 7. CREACION DE PCA (para visualizaciones futuras)
    print("\n" + "="*100)
    print("FASE 6: REDUCCION DIMENSIONAL (PCA)")
    print("="*100)
    
    pca, features_pca = crear_pca_visualizacion(features_scaled, n_components=2)
    
    # 8. GUARDADO DE MODELOS Y RESULTADOS
    print("\n" + "="*100)
    print("FASE 7: GUARDADO DE MODELOS Y GENERACION DE REPORTES")
    print("="*100)
    
    # Guardar modelos
    rutas_modelos = guardar_modelos_clustering(
        kmeans, scaler, pca, n_clusters, directorio_modelos
    )
    
    # Exportar datos segmentados
    ruta_csv = exportar_datos_segmentados(
        df_con_clusters, n_clusters, directorio_datos
    )
    
    # Generar reportes CSV
    ruta_resumen_csv = generar_resumen_ejecutivo_csv(
        interpretaciones, n_clusters, directorio_datos, df_con_clusters
    )
    
    ruta_acciones = generar_acciones_comerciales_por_cluster(
        df_con_clusters, interpretaciones, n_clusters, directorio_datos
    )
    
    # 9. RESUMEN FINAL
    fin_pipeline = datetime.now()
    duracion = (fin_pipeline - inicio_pipeline).total_seconds()
    
    print("\n" + "="*100)
    print("PIPELINE COMPLETADO EXITOSAMENTE")
    print("="*100)
    print(f"\nTiempo total de ejecuci�n: {duracion:.2f} segundos")
    print(f"\nARCHIVOS GENERADOS:")
    print(f"  Modelos:")
    print(f"    - K-Means: {rutas_modelos['kmeans']}")
    print(f"    - Scaler: {rutas_modelos['scaler']}")
    print(f"    - PCA: {rutas_modelos['pca']}")
    print(f"  Datos:")
    print(f"    - Clientes segmentados: {ruta_csv}")
    print(f"  Reportes:")
    print(f"    - Resumen ejecutivo (CSV): {ruta_resumen_csv}")
    print(f"    - Acciones comerciales (CSV): {ruta_acciones}")
    
    print(f"\nMETRICAS FINALES DEL MODELO:")
    print(f"  - Numero de clusters: {n_clusters}")
    print(f"  - Silhouette Score: {metricas['silhouette_score']:.4f}")
    print(f"  - Davies-Bouldin Index: {metricas['davies_bouldin_score']:.4f}")
    print(f"  - Calinski-Harabasz Score: {metricas['calinski_harabasz_score']:.2f}")
    print(f"  - Inertia: {metricas['inertia']:.2f}")
    
    print("\n" + "="*100)
    
    return {
        'metricas': metricas,
        'interpretaciones': interpretaciones,
        'rutas_modelos': rutas_modelos,
        'ruta_datos_segmentados': ruta_csv,
        'rutas_reportes': {
            'resumen_csv': ruta_resumen_csv,
            'acciones_csv': ruta_acciones
        }
    }


def main():
    """
    Funcion principal con argumentos de linea de comandos.
    """
    parser = argparse.ArgumentParser(
        description='Pipeline de segmentacion K-Means para clientes mayoristas'
    )
    
    parser.add_argument(
        '--datos',
        type=str,
        default='data/processed/metricas_clientes_ml.csv',
        help='Ruta al archivo CSV con los datos (default: data/processed/metricas_clientes_ml.csv)'
    )
    
    parser.add_argument(
        '--k',
        type=int,
        default=None,
        help='Numero de clusters (si no se especifica, se usa analisis automatico)'
    )
    
    parser.add_argument(
        '--no-analizar-k',
        action='store_true',
        help='No realizar analisis de k optimo (mas rapido)'
    )
    
    parser.add_argument(
        '--dir-modelos',
        type=str,
        default='models',
        help='Directorio para guardar modelos (default: models)'
    )
    
    parser.add_argument(
        '--dir-datos',
        type=str,
        default='data/processed',
        help='Directorio para guardar datos procesados (default: data/processed)'
    )
    
    args = parser.parse_args()
    
    # Ejecutar pipeline
    try:
        resultados = ejecutar_pipeline_completo(
            DATA_PATH=args.datos,
            n_clusters=args.k,
            analizar_k_optimo=not args.no_analizar_k,
            directorio_modelos=args.dir_modelos,
            directorio_datos=args.dir_datos
        )
        
        print("\n[EXITO] Pipeline ejecutado correctamente")
        sys.exit(0)
        
    except Exception as e:
        print(f"\n[ERROR CRITICO] Error durante la ejecucion del pipeline:")
        print(f"  {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()