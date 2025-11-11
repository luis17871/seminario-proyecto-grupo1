"""
API de Segmentacion de Clientes Mayoristas
==========================================
API desarrollada con FastAPI para gestionar la segmentacion de clientes.

Endpoints:
- GET /segments/summary: Obtiene resumen de caracteristicas de cada segmento
- POST /segments/classify: Clasifica un nuevo cliente en un segmento

Autor: Seminario - Grupo 1
Fecha: Noviembre 2025
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
import logging

# Configuracion de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar FastAPI
app = FastAPI(
    title="API de Segmentacion de Clientes Mayoristas",
    description="API para obtener resumen de segmentos y clasificar nuevos clientes",
    version="1.0.0"
)

# Configurar CORS para permitir peticiones desde cualquier origen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todos los origenes (para produccion, especifica los dominios)
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los metodos (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos los headers
)

# Directorios
BASE_DIR = Path(__file__).parent
MODELS_DIR = BASE_DIR / "models"
DATA_DIR = BASE_DIR / "data" / "processed"

# Variables globales para modelos
kmeans_model = None
scaler_model = None
pca_model = None
segmentos_info = None
df_segmentados = None


# ============================================================================
# MODELOS PYDANTIC
# ============================================================================

class ClienteInput(BaseModel):
    """Modelo de entrada para clasificar un nuevo cliente"""
    recency: float = Field(..., description="Dias desde la ultima compra", ge=0)
    frequency: int = Field(..., description="Numero total de compras", ge=1)
    monetary: float = Field(..., description="Valor total de compras en $", gt=0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "recency": 15,
                "frequency": 150,
                "monetary": 5000.50
            }
        }


class ClienteClasificado(BaseModel):
    """Modelo de respuesta para un cliente clasificado"""
    recency: float
    frequency: int
    monetary: float
    RFM_Score: float
    cluster_id: int
    nombre_segmento: str
    estrategia_comercial: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "recency": 15,
                "frequency": 150,
                "monetary": 5000.50,
                "RFM_Score": 85.75,
                "cluster_id": 1,
                "nombre_segmento": "Clientes Leales",
                "estrategia_comercial": "Programa de fidelizacion con beneficios progresivos..."
            }
        }


class SegmentoResumen(BaseModel):
    """Modelo de resumen de un segmento"""
    cluster_id: int
    nombre_segmento: str
    estrategia_comercial: str
    n_clientes: int
    porcentaje_total: float
    caracteristicas: Dict[str, float]
    
    class Config:
        json_schema_extra = {
            "example": {
                "cluster_id": 1,
                "nombre_segmento": "Clientes Leales",
                "estrategia_comercial": "Programa de fidelizacion...",
                "n_clientes": 2905,
                "porcentaje_total": 49.6,
                "caracteristicas": {
                    "recency_promedio": 45.2,
                    "frequency_promedio": 120.5,
                    "monetary_promedio": 4500.80,
                    "RFM_Score_promedio": 82.5
                }
            }
        }


class SegmentosResponse(BaseModel):
    """Modelo de respuesta para el resumen de todos los segmentos"""
    total_clientes: int
    n_segmentos: int
    segmentos: List[SegmentoResumen]


# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def cargar_modelos():
    """Carga los modelos de clustering y segmentacion"""
    global kmeans_model, scaler_model, pca_model, segmentos_info, df_segmentados
    
    try:
        logger.info("Cargando modelos...")
        
        # Cargar modelo KMeans
        kmeans_path = MODELS_DIR / "kmeans_model_k3.joblib"
        if not kmeans_path.exists():
            raise FileNotFoundError(f"Modelo KMeans no encontrado en {kmeans_path}")
        kmeans_model = joblib.load(kmeans_path)
        logger.info(f"? Modelo KMeans cargado: {kmeans_model.n_clusters} clusters")
        
        # Cargar Scaler
        scaler_path = MODELS_DIR / "scaler_kmeans_k3.joblib"
        if not scaler_path.exists():
            raise FileNotFoundError(f"Scaler no encontrado en {scaler_path}")
        scaler_model = joblib.load(scaler_path)
        logger.info("? Scaler cargado")
        
        # Cargar PCA (opcional - solo para visualizacion, NO para prediccion)
        # NOTA: El modelo KMeans fue entrenado con las 7 features escaladas (sin PCA)
        # El PCA solo se usa para visualizacion 2D en notebooks/dashboards
        pca_path = MODELS_DIR / "pca_kmeans_k3.joblib"
        if pca_path.exists():
            pca_model = joblib.load(pca_path)
            logger.info("? PCA cargado (solo para visualizacion)")
        else:
            pca_model = None
            logger.warning("? PCA no encontrado (no es necesario para clasificacion)")
        
        # Cargar datos segmentados
        segmentados_path = DATA_DIR / "clientes_mayoristas_segmentados_k3.csv"
        if not segmentados_path.exists():
            raise FileNotFoundError(f"Datos segmentados no encontrados en {segmentados_path}")
        df_segmentados = pd.read_csv(segmentados_path)
        logger.info(f"? Datos segmentados cargados: {len(df_segmentados)} clientes")
        
        # Cargar resumen ejecutivo
        resumen_files = sorted(DATA_DIR.glob("resumen_ejecutivo_k3_*.csv"))
        if resumen_files:
            resumen_path = resumen_files[-1]  # Tomar el mas reciente
        else:
            resumen_path = DATA_DIR / "resumen_ejecutivo_k3.csv"
        
        if not resumen_path.exists():
            raise FileNotFoundError(f"Resumen ejecutivo no encontrado en {resumen_path}")
        
        df_resumen = pd.read_csv(resumen_path)
        segmentos_info = df_resumen.to_dict('records')
        logger.info(f"? Resumen ejecutivo cargado: {len(segmentos_info)} segmentos")
        
        logger.info("="*80)
        logger.info("MODELOS CARGADOS EXITOSAMENTE")
        logger.info("="*80)
        
    except Exception as e:
        logger.error(f"ERROR al cargar modelos: {e}")
        raise


def calcular_rfm_score(recency: float, frequency: int, monetary: float) -> float:
    """
    Calcula el RFM Score basado en percentiles del dataset de referencia
    
    Parametros:
    -----------
    recency : float
        Dias desde la ultima compra
    frequency : int
        Numero de compras
    monetary : float
        Valor total de compras
        
    Retorna:
    --------
    float
        RFM Score calculado (0-100)
    """
    if df_segmentados is None:
        raise ValueError("Datos de referencia no cargados")
    
    # Calcular percentiles basados en los datos existentes
    # Recency: menor es mejor (invertir)
    r_rank = 100 - (df_segmentados['recency'] <= recency).sum() / len(df_segmentados) * 100
    
    # Frequency: mayor es mejor
    f_rank = (df_segmentados['frequency'] <= frequency).sum() / len(df_segmentados) * 100
    
    # Monetary: mayor es mejor
    m_rank = (df_segmentados['monetary'] <= monetary).sum() / len(df_segmentados) * 100
    
    # Promedio ponderado (igual peso para todos)
    rfm_score = (r_rank + f_rank + m_rank) / 3
    
    return round(rfm_score, 2)


def clasificar_cliente(recency: float, frequency: int, monetary: float) -> Dict:
    """
    Clasifica un cliente en un segmento basado en sus datos RFM
    
    Parametros:
    -----------
    recency : float
        Dias desde la ultima compra
    frequency : int
        Numero de compras
    monetary : float
        Valor total de compras
        
    Retorna:
    --------
    Dict
        Diccionario con la clasificacion completa del cliente
    """
    if kmeans_model is None or scaler_model is None:
        raise ValueError("Modelos no cargados")
    
    # Calcular RFM Score
    rfm_score = calcular_rfm_score(recency, frequency, monetary)
    
    # Calcular ranks normalizados (percentiles)
    r_rank_norm = 100 - (df_segmentados['recency'] <= recency).sum() / len(df_segmentados) * 100
    f_rank_norm = (df_segmentados['frequency'] <= frequency).sum() / len(df_segmentados) * 100
    m_rank_norm = (df_segmentados['monetary'] <= monetary).sum() / len(df_segmentados) * 100
    
    # Preparar datos para prediccion (7 features en el orden correcto)
    # Las features usadas en el entrenamiento son:
    # ['recency', 'frequency', 'monetary', 'R_rank_norm', 'F_rank_norm', 'M_rank_norm', 'RFM_Score']
    features_df = pd.DataFrame({
        'recency': [recency],
        'frequency': [frequency],
        'monetary': [monetary],
        'R_rank_norm': [r_rank_norm],
        'F_rank_norm': [f_rank_norm],
        'M_rank_norm': [m_rank_norm],
        'RFM_Score': [rfm_score]
    })
    
    # Normalizar usando el scaler entrenado
    features_scaled = scaler_model.transform(features_df)
    
    # IMPORTANTE: NO aplicar PCA para prediccion
    # El modelo KMeans fue entrenado con las 7 features escaladas (sin PCA)
    # El PCA solo se usa para visualizacion 2D, no para prediccion
    
    # Predecir cluster directamente con las features escaladas
    cluster_id = int(kmeans_model.predict(features_scaled)[0])
    
    # Obtener informacion del segmento
    segmento = next((s for s in segmentos_info if s['cluster_id'] == cluster_id), None)
    
    if segmento is None:
        raise ValueError(f"Segmento {cluster_id} no encontrado en datos de referencia")
    
    return {
        'recency': recency,
        'frequency': frequency,
        'monetary': monetary,
        'RFM_Score': rfm_score,
        'cluster_id': cluster_id,
        'nombre_segmento': segmento['nombre_segmento'],
        'estrategia_comercial': segmento['estrategia_comercial']
    }


# ============================================================================
# EVENTOS DE INICIO/CIERRE
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Evento que se ejecuta al iniciar la aplicacion"""
    logger.info("Iniciando API de Segmentacion de Clientes...")
    cargar_modelos()


@app.on_event("shutdown")
async def shutdown_event():
    """Evento que se ejecuta al cerrar la aplicacion"""
    logger.info("Cerrando API de Segmentacion de Clientes...")


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/", tags=["General"])
def root():
    """Endpoint raiz con informacion de la API"""
    return {
        "message": "API de Segmentacion de Clientes Mayoristas",
        "version": "1.0.0",
        "endpoints": {
            "resumen_segmentos": "/segments/summary",
            "clasificar_cliente": "/segments/classify",
            "documentacion": "/docs"
        }
    }


@app.get("segments/summary", response_model=SegmentosResponse, tags=["Segmentos"])
def obtener_resumen_segmentos():
    """
    Obtiene un resumen de las caracteristicas de cada segmento
    
    Retorna:
    --------
    SegmentosResponse
        Objeto con informacion completa de todos los segmentos:
        - Total de clientes
        - Numero de segmentos
        - Lista de segmentos con sus caracteristicas
    
    Errores:
    --------
    - 500: Error al cargar datos de segmentos
    """
    try:
        if df_segmentados is None or segmentos_info is None:
            raise HTTPException(status_code=500, detail="Datos de segmentos no cargados")
        
        # Calcular estadisticas por segmento
        segmentos_detallados = []
        
        for segmento in segmentos_info:
            cluster_id = segmento['cluster_id']
            
            # Filtrar datos del cluster
            cluster_data = df_segmentados[df_segmentados['segment'] == cluster_id]
            
            # Calcular caracteristicas
            caracteristicas = {
                'recency_promedio': round(cluster_data['recency'].mean(), 2),
                'recency_mediana': round(cluster_data['recency'].median(), 2),
                'frequency_promedio': round(cluster_data['frequency'].mean(), 2),
                'frequency_mediana': round(cluster_data['frequency'].median(), 2),
                'monetary_promedio': round(cluster_data['monetary'].mean(), 2),
                'monetary_mediana': round(cluster_data['monetary'].median(), 2),
                'RFM_Score_promedio': round(cluster_data['RFM_Score'].mean(), 2),
                'RFM_Score_mediana': round(cluster_data['RFM_Score'].median(), 2)
            }
            
            # Crear objeto de segmento
            segmento_detallado = SegmentoResumen(
                cluster_id=cluster_id,
                nombre_segmento=segmento['nombre_segmento'],
                estrategia_comercial=segmento['estrategia_comercial'],
                n_clientes=len(cluster_data),
                porcentaje_total=round((len(cluster_data) / len(df_segmentados)) * 100, 2),
                caracteristicas=caracteristicas
            )
            
            segmentos_detallados.append(segmento_detallado)
        
        # Ordenar por cluster_id
        segmentos_detallados.sort(key=lambda x: x.cluster_id)
        
        return SegmentosResponse(
            total_clientes=len(df_segmentados),
            n_segmentos=len(segmentos_info),
            segmentos=segmentos_detallados
        )
        
    except Exception as e:
        logger.error(f"Error al obtener resumen de segmentos: {e}")
        raise HTTPException(status_code=500, detail=f"Error al obtener resumen: {str(e)}")


@app.post("segments/classify", response_model=ClienteClasificado, tags=["Segmentos"])
def clasificar_nuevo_cliente(cliente: ClienteInput):
    """
    Clasifica un nuevo cliente en un segmento basado en sus datos RFM
    
    Parametros:
    -----------
    cliente : ClienteInput
        Datos del cliente a clasificar:
        - recency: Dias desde la ultima compra (>= 0)
        - frequency: Numero total de compras (>= 1)
        - monetary: Valor total de compras en $ (> 0)
    
    Retorna:
    --------
    ClienteClasificado
        Objeto con la clasificacion completa del cliente:
        - Datos originales (recency, frequency, monetary)
        - RFM Score calculado
        - Cluster asignado
        - Nombre del segmento
        - Estrategia comercial recomendada
    
    Errores:
    --------
    - 400: Datos de entrada invalidos
    - 500: Error en el proceso de clasificacion
    """
    try:
        # Validaciones adicionales
        if cliente.recency < 0:
            raise HTTPException(status_code=400, detail="Recency debe ser >= 0")
        if cliente.frequency < 1:
            raise HTTPException(status_code=400, detail="Frequency debe ser >= 1")
        if cliente.monetary <= 0:
            raise HTTPException(status_code=400, detail="Monetary debe ser > 0")
        
        # Clasificar cliente
        resultado = clasificar_cliente(
            recency=cliente.recency,
            frequency=cliente.frequency,
            monetary=cliente.monetary
        )
        
        logger.info(f"Cliente clasificado: Segmento {resultado['cluster_id']} - {resultado['nombre_segmento']}")
        
        return ClienteClasificado(**resultado)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al clasificar cliente: {e}")
        raise HTTPException(status_code=500, detail=f"Error al clasificar cliente: {str(e)}")


@app.get("/health", tags=["General"])
def health_check():
    """Endpoint de health check para verificar el estado de la API"""
    return {
        "status": "healthy",
        "modelos_cargados": {
            "kmeans": kmeans_model is not None,
            "scaler": scaler_model is not None,
            "pca": pca_model is not None,
            "datos_segmentados": df_segmentados is not None,
            "segmentos_info": segmentos_info is not None
        }
    }


# # ============================================================================
# # EJECUCION
# # ============================================================================

# if __name__ == "__main__":
#     import uvicorn
    
#     print("\n" + "="*80)
#     print("INICIANDO API DE SEGMENTACION DE CLIENTES")
#     print("="*80)
#     print("\nEndpoints disponibles:")
#     print("  - http://localhost:8000/segments/summary")
#     print("  - http://localhost:8000/segments/classify")
#     print("  - http://localhost:8000/docs (documentacion interactiva)")
#     print("\n" + "="*80 + "\n")
    
#     uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
