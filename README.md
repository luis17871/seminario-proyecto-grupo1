# Segmentación de Clientes para una Cadena de Retail

**Seminario Complexivo – UNIANDES**

🧩 Proyecto de segmentación de clientes mayoristas basado en métricas RFM y clustering K-Means, expuesto mediante una API en FastAPI y un dashboard interactivo en Streamlit.

## 🧭 Tema del caso y Objetivo

**Tema del caso:** Segmentación de Clientes para una Cadena de Retail

**Antecedentes:** El dataset a utilizar (Online Retail II) contiene el historial de transacciones reales de una empresa de comercio electrónico con sede en el Reino Unido, registradas entre 2009 y 2011. La compañía vende principalmente regalos y artículos para el hogar a clientes mayoristas (otras empresas). Como en cualquier negocio, no todos los clientes son iguales, y la gerencia necesita una forma, basada en datos, para comprender su base de clientes e identificar a los más valiosos para optimizar sus esfuerzos de marketing y la gestión de sus cuentas clave.

**Objetivo:** Construir un sistema analítico que utilice técnicas de clustering (K-Means) para segmentar a los clientes mayoristas en grupos coherentes basados en su comportamiento de compra (Recencia, Frecuencia, Valor Monetario - RFM). El objetivo es proveer a la empresa una herramienta para identificar a sus "Clientes VIP", "Clientes leales", "Clientes en Riesgo", etc.

## 📚 Descripción general del proyecto

Este repositorio implementa de principio a fin un sistema analítico de segmentación de clientes para una cadena de retail mayorista, siguiendo el caso del dataset Online Retail II de Kaggle. A partir de las transacciones históricas se construye un pipeline de datos + modelo de machine learning + API + dashboard, con tres componentes principales:

### 1. Pipeline de datos (ETL + RFM)

   * Limpieza avanzada del dataset de ventas.
   * Cálculo de métricas RFM (Recency, Frequency, Monetary) por cliente.
   * Generación de un dataset listo para machine learning.

### 2. Modelo de segmentación (K-Means)

   * Preparación y normalización de las features de clustering.
   * Búsqueda del número óptimo de clusters.
   * Entrenamiento de un modelo K-Means.
   * Asignación de cada cliente a un segmento (Clientes VIP, Leales, en Riesgo, etc.).
   * Exportación de modelos y reportes ejecutivos para negocio.

### 3. Capa de consumo (API + Dashboard)

   * API en FastAPI para:
     * Obtener un resumen ejecutivo de los segmentos (GET /segments/summary).
     * Clasificar un nuevo cliente en un segmento a partir de sus datos RFM (POST /segments/classify).
   * Dashboard en Streamlit que:
     * Muestra un EDA de ventas y clientes.
     * Explora las métricas RFM.
     * Visualiza los clusters (incluyendo un gráfico 3D RFM).
     * Permite clasificar clientes de forma interactiva usando la API.

## 👥 Equipo

* Fernando Xavier Carrión Tabango

* Brayan Alejandro Morán Chandi

* Luis Ernesto Caicedo Mendoza

## 🧩 Conceptos clave

### ¿Qué es RFM?

* **Recency (R):** Días desde la última compra del cliente.

* **Frequency (F):** Número de compras (facturas) realizadas.

* **Monetary (M):** Monto total gastado por el cliente.

En este proyecto:

* Se calculan métricas RFM a nivel de cliente.

* Se estandarizan mediante rankings normalizados (R_rank_norm, F_rank_norm, M_rank_norm).

* Se construye un RFM_Score ponderado (15% R, 28% F, 57% M) para reflejar la importancia del valor monetario en el negocio mayorista.

### ¿Qué hace K-Means aquí?

* Toma como entrada las features numéricas (R, F, M, ranks normalizados, RFM_Score).

* Agrupa clientes en k clusters según su comportamiento.

* Los clusters se ordenan por RFM_Score promedio y se etiquetan con nombres de negocio:

  * Clientes VIP
  * Clientes Leales
  * Clientes Regulares / Prometedores
  * Clientes en Riesgo
  * (Según el número de clusters elegido)

## 🏗️ Arquitectura general

### 1. Datos de entrada

   * Dataset original: Online Retail II (Kaggle).
   * En el proyecto se utiliza un archivo data/BASERETAIL.csv, que es una versión limpia/adaptada para el seminario.

### 2. Pipeline ETL + RFM (main.py + módulo scripts/)

   1. Cargar datos brutos (BASERETAIL.csv).
   2. Limpiar y normalizar columnas, tipos de datos, fechas, cancelaciones, precios, códigos, etc. (data_cleaning.py).
   3. Generar métricas RFM y score (data_new_feautures_edit.py).
   4. Guardar resultados procesados:
      * data/processed/clientes_limpios.csv
      * data/processed/metricas_clientes_ml.csv

### 3. Pipeline de modelado y segmentación (train.py + módulos de modelo)

   1. Cargar métricas RFM (metricas_clientes_ml.csv).
   2. Preparar features para clustering y normalizarlas (model_preprocessing.py).
   3. Analizar número óptimo de clusters (método del codo y Silhouette).
   4. Entrenar modelo K-Means (model_training.py).
   5. Asignar cluster/segmento a cada cliente.
   6. Generar interpretaciones de negocio para cada cluster.
   7. Guardar modelos y datos segmentados:
      * Modelos: models/kmeans_model_k{K}.joblib, scaler_kmeans_k{K}.joblib, pca_kmeans_k{K}.joblib.
      * Datos segmentados: data/processed/clientes_mayoristas_segmentados_k{K}.csv.
      * Resumen ejecutivo por segmento: data/processed/resumen_ejecutivo_k{K}.csv.
      * Acciones comerciales recomendadas por cliente: data/processed/acciones_comerciales_k{K}.csv.

### 4. API de segmentación (api_segmentacion.py)

   * Carga los modelos entrenados (actualmente se asume K=3 → archivos con sufijo k3).
   * Usa el dataset segmentado como referencia para calcular percentiles RFM.
   * Exponde endpoints REST para consumo desde aplicaciones externas o el dashboard.

### 5. Dashboard interactivo (dashboard_app.py + assets/styles.css)

   * Tab 1 – EDA (Análisis Exploratorio) sobre clientes_limpios.csv:
     * KPIs de negocio (ventas totales, #clientes, #facturas, #productos).
     * Evolución de ventas por mes.
     * Top 10 productos.
     * Ventas por país y mapa geográfico.
   * Tab 2 – RFM + Segmentación:
     * Entrenar modelo de clustering desde la interfaz.
     * Conectarse a la API para obtener resumen de segmentos.
     * Clasificador interactivo de nuevos clientes.
     * Visualización 3D de clusters en espacio RFM.
     * Tablas resumen e insights de valor por segmento.

## 📂 Estructura del repositorio
```
seminario-proyecto-grupo1/
│
├── data/
│   ├── BASERETAIL.csv                # Base de transacciones (derivada de Online Retail II)
│   └── processed/
│       ├── clientes_limpios.csv      # Ventas limpias a nivel transacción
│       ├── metricas_clientes_ml.csv  # Métricas RFM por cliente (input para ML)
│       ├── clientes_mayoristas_segmentados_k3.csv   # Clientes con cluster asignado
│       ├── resumen_ejecutivo_k3.csv              # Resumen ejecutivo por segmento
│       └── acciones_comerciales_k3.csv           # Recomendaciones por cliente
│
├── scripts/
│   ├── data_loader.py               # Carga BASERETAIL.csv
│   ├── data_cleaning.py             # Limpieza y normalización del dataset
│   ├── imputation.py                # Imputación genérica de valores nulos (opcional)
│   ├── data_new_feautures_edit.py   # Cálculo detallado de RFM + RFM_Score
│   ├── data_new_features.py         # Versión alternativa basada en cuantiles y reglas
│   ├── data_saving.py               # Funciones para guardar CSV procesados
│   ├── model_preprocessing.py       # Preparación y normalización de features
│   ├── model_training.py            # Entrenamiento K-Means e interpretación de clusters
│   └── model_saving.py              # Guardado de modelos y reportes ejecutivos
│
├── assets/
│   └── styles.css                   # Estilos personalizados para el dashboard (tema oscuro)
│
├── main.py                          # Pipeline general de datos (ETL + RFM)
├── train.py                         # Pipeline general de entrenamiento y segmentación
├── api_segmentacion.py              # API FastAPI para resumen & clasificación de segmentos
├── dashboard_app.py                 # Dashboard Streamlit (EDA + RFM + Segmentos)
├── requirements.txt                 # Dependencias del proyecto
├── devcontainer.json                # Configuración para GitHub Codespaces / Dev Containers
└── README.md                        # Este archivo
```

## 🧪 Flujo detallado del pipeline de datos

### 1. Carga de datos (scripts/data_loader.py)

* Usa pandas.read_csv para leer data/BASERETAIL.csv.

* Maneja errores comunes (archivo no encontrado, errores inesperados).

* Devuelve un DataFrame con las transacciones brutas.

### 2. Limpieza de datos (scripts/data_cleaning.py)

Principales transformaciones:

* **Renombrado y normalización de columnas**

  * Cambia nombres originales (Invoice, StockCode, Description, etc.) a nombres consistentes (invoice_number, product_code, etc.) y los pasa a minúsculas.

* **Tipos de datos**

  * Convierte customer_id a Int64.
  * Convierte product_quantity a entero.
  * Convierte product_price a float con 2 decimales.
  * Convierte product_code a str.
  * Normaliza invoice_date a tipo datetime sin hora.

* **Manejo de datos faltantes**

  * Elimina filas sin customer_id.

* **Calidad de datos**

  * Elimina transacciones de cancelación/devoluciones (facturas/filas con cantidades negativas).
  * Elimina precios negativos o cero.
  * Normaliza descripciones de producto (minúsculas, strip()).
  * Homogeneiza países (por ejemplo, EIRE → Ireland).
  * Filtra códigos de producto de pruebas, cargos bancarios, ajustes, etc.

El resultado se guarda como clientes_limpios.csv.

### 3. Cálculo de métricas RFM (scripts/data_new_feautures_edit.py)

Sobre el DataFrame limpio se realizan los siguientes pasos:

1. **Normalización de fechas (normalizar_fechas)**

   * Asegura que invoice_date sea datetime.

2. **Recency (calcular_recency)**

   * Agrupa por customer_id y toma la fecha máxima de compra (última compra).
   * Calcula días desde la última compra respecto a la fecha más reciente del dataset.

3. **Frequency (calcular_frecuency)**

   * Cuenta cuántas facturas/combos únicos (invoice_number, product_code, customer_id) tiene cada cliente.

4. **Monetary (calcular_monetary)**

   * Calcula TotalSum = product_price * product_quantity por línea.
   * Agrupa por customer_id y suma TotalSum para obtener el valor monetario total.

5. **Construcción del DataFrame RFM (construir_rfm)**

   * Une recency, frequency y monetary.
   * Calcula ranks para cada métrica:
     * R_rank, F_rank, M_rank.
   * Normaliza esos rangos a escala 0–100:
     * R_rank_norm, F_rank_norm, M_rank_norm.
   * Calcula RFM_Score como combinación ponderada de los tres.
   * Redondea todo a 2 decimales.

El resultado se guarda como metricas_clientes_ml.csv y es la base para el modelo de clustering.

## 🤖 Pipeline de modelado y segmentación (K-Means)

### 1. Preprocesamiento de features (scripts/model_preprocessing.py)

* **preparar_features_clustering(df)**

  * Separa customer_id de las features (para no usarlo en el clustering).
  * Deja solo columnas numéricas relevantes (R, F, M, ranks, RFM_Score).

* **normalizar_features(features)**

  * Aplica StandardScaler para llevar todas las variables a media 0 y sigma 1.
  * Devuelve:
    * features_scaled (array NumPy).
    * scaler entrenado (usado luego en API para nuevos clientes).
    * features_scaled_df (DataFrame escalado).

* **analizar_numero_optimo_clusters**

  * Evalúa K desde k_min hasta k_max (por defecto 2–10).
  * Para cada K calcula:
    * WCSS (Within-Cluster Sum of Squares – método del codo).
    * Silhouette Score (calidad de separación).
  * Elige como k recomendado el que maximiza el Silhouette Score.

* **crear_pca_visualizacion**

  * Crea un PCA de 2 componentes para facilitar visualizaciones 2D.
  * Se utiliza en Dashboard y análisis exploratorios.

### 2. Entrenamiento del modelo (scripts/model_training.py)

* **entrenar_kmeans**

  * Entrena un modelo K-Means con:
    * Número de clusters n_clusters.
    * random_state, n_init, max_iter.
  * Devuelve:
    * kmeans entrenado.
    * Métricas de evaluación:
      * Silhouette Score
      * Davies–Bouldin Index
      * Calinski–Harabasz Score
      * Inertia

* **asignar_clusters_a_dataframe**

  * Agrega una columna segment al DataFrame original indicando el cluster asignado.
  * Muestra la distribución de clientes por cluster.

* **generar_interpretaciones_todos_clusters**

  * Calcula el RFM_Score promedio por cluster.
  * Ordena los clusters de mayor a menor RFM.
  * Asigna un nombre de segmento según su posición:
    * Ejemplo con 3 clusters:
      * Cluster con mayor RFM → Clientes VIP.
      * Segundo → Clientes Leales.
      * Tercero → Clientes en riesgo.
  * Define un texto de estrategia comercial para cada segmento:
    * Clientes VIP: condiciones comerciales premium, gerente de cuenta dedicado, etc.
    * Leales: programas de fidelización, cross-selling, etc.
    * En riesgo: campañas de recuperación, contacto proactivo, etc.

### 3. Guardado de modelos y reportes (scripts/model_saving.py)

* **Modelos (guardar_modelos_clustering)**

  * Guarda:
    * kmeans_model_k{K}.joblib
    * scaler_kmeans_k{K}.joblib
    * pca_kmeans_k{K}.joblib

* **Datos segmentados (exportar_datos_segmentados)**

  * Crea clientes_mayoristas_segmentados_k{K}.csv con:
    * customer_id, métricas RFM, RFM_Score, segment.

* **Resumen ejecutivo (generar_resumen_ejecutivo_csv)**

  * Crea resumen_ejecutivo_k{K}.csv con:
    * cluster_id, nombre_segmento, % clientes, estrategia comercial.

* **Acciones comerciales por cluster (generar_acciones_comerciales_por_cluster)**

  * Crea acciones_comerciales_k{K}.csv con:
    * customer_id, segment, nombre_segmento, estrategia_comercial.

## 🌐 API de segmentación (FastAPI)

**Archivo principal:** api_segmentacion.py

### Modelos de datos (Pydantic)

* **ClienteInput**  
Cuerpo de la petición para clasificar un cliente:
```
{
  "recency": 15,
  "frequency": 150,
  "monetary": 5000.50
}
```

* **ClienteClasificado**  
Respuesta de clasificación:
```
{
  "recency": 15,
  "frequency": 150,
  "monetary": 5000.5,
  "RFM_Score": 85.75,
  "cluster_id": 1,
  "nombre_segmento": "Clientes Leales",
  "estrategia_comercial": "Programa de fidelizacion con beneficios progresivos..."
}
```

* **SegmentosResponse / SegmentoResumen**  
Estructuras para el resumen de segmentos.

### Endpoints principales

1. **GET /**

   * Información básica de la API (mensaje, versión, lista de endpoints).

2. **GET /health**

   * Verifica el estado de la API y si los modelos/datos fueron cargados correctamente.

3. **GET /segments/summary**

   * Devuelve:
     * total_clientes
     * n_segmentos
     * Lista de segmentos con:
       * cluster_id, nombre_segmento, estrategia_comercial
       * n_clientes, porcentaje_total
       * Métricas promedio y mediana:
         * recency, frequency, monetary, RFM_Score

4. **POST /segments/classify**

   * Recibe datos RFM de un cliente.
   * Calcula un nuevo RFM_Score basándose en percentiles de la población.
   * Escala las 7 features [recency, frequency, monetary, R_rank_norm, F_rank_norm, M_rank_norm, RFM_Score].
   * Usa el modelo K-Means entrenado para asignar un cluster_id.
   * Devuelve:
     * cluster_id, nombre_segmento, estrategia_comercial recomendada.
     * Datos RFM y RFM_Score del cliente.

⚙️ **Tecnología:**

* Backend: FastAPI

* Serialización: Pydantic

* Modelos: joblib + scikit-learn

* CORS habilitado para permitir uso desde el Dashboard.

## 📊 Dashboard interactivo (Streamlit)

**Archivo principal:** dashboard_app.py  
**Estilos:** assets/styles.css (tema oscuro con glassmorphism, gradientes, métricas en tarjetas).

### Tab 1 – Análisis Exploratorio (EDA)

* **Filtros interactivos**

  * País (multiselect).
  * Rango de fechas (slider).

* **KPIs**

  * Ventas totales.
  * Número de facturas.
  * Número de clientes únicos.
  * Número de productos.

* **Visualizaciones**

  * Evolución de ventas mensuales (gráfico de área).
  * Top 10 productos por cantidad vendida (barras horizontales).
  * Ventas por país (barras).
  * Mapa geográfico de ventas (choropleth por país).

### Tab 2 – Métricas RFM & Segmentación

1. **Entrenamiento del modelo K-Means desde el dashboard**

   * Botón: ENTRENAR MODELO K-MEANS
   * Muestra:
     * Barra de progreso del pipeline (del 1/7 al 7/7).
     * Métricas del modelo entrenado:
       * Número de clusters.
       * Silhouette Score.
       * Davies–Bouldin.
       * Calinski–Harabasz.
       * Número de clientes.

2. **Conexión con la API**

   * Verifica si la API está activa (/health).
   * Si está disponible:
     * Muestra resumen de segmentos (tarjetas + expanders por segmento).
     * Gráficos:
       * Pie chart de distribución de clientes por segmento.
       * Barras de RFM_Score promedio.
       * Comparación normalizada de R, F, M entre segmentos.
       * Líneas para visualizar el perfil de cada segmento.

3. **Clasificador de nuevos clientes**

   * Inputs:
     * Recency (días desde la última compra).
     * Frequency (número de compras).
     * Monetary (valor total).
   * Llama al endpoint /segments/classify.
   * Muestra:
     * Segmento asignado y RFM_Score del cliente.
     * Estrategia comercial recomendada.
     * Comparación vs promedio del segmento en %.

4. **Visualización 3D de segmentos RFM**

   * Usa clientes_mayoristas_segmentados_k3.csv.
   * Gráfico Scatter3D (Plotly) con:
     * Ejes: Recency, Frequency, Monetary.
     * Color por segmento.
     * Tooltip con customer_id y RFM_Score.

5. **Dashboard de segmentación & estrategias**

   * Pie chart de clientes por segmento.
   * Tabla de estrategias por segmento (desde resumen_ejecutivo_k3.csv).
   * Gráficos comparando métricas promedio por segmento.
   * Análisis de valor total, ticket promedio, número de clientes, potencial de crecimiento.

## 🛠️ Tecnologías utilizadas

* **Lenguaje**

  * Python 3.9+

* **Procesamiento y análisis de datos**

  * pandas, numpy

* **Machine Learning**

  * scikit-learn (StandardScaler, KMeans, métricas de clustering, PCA)
  * joblib (persistencia de modelos)

* **Visualización**

  * plotly, plotly.express, plotly.graph_objects
  * matplotlib (en módulos auxiliares)

* **Dashboard**

  * streamlit

* **API**

  * fastapi
  * uvicorn

* **Entorno**

  * devcontainer.json para entorno reproducible (GitHub Codespaces / VS Code Dev Containers).

## 🚀 Instalación y ejecución

### 1. Clonar el repositorio
```
git clone https://github.com/luis17871/seminario-proyecto-grupo1.git
cd seminario-proyecto-grupo1
```

### 2. Crear entorno virtual
```
python -m venv venv
# Windows
venv\Scripts\activate
# Linux / macOS
source venv/bin/activate
```

### 3. Instalar dependencias
```
pip install -r requirements.txt
```

### 4. Preparar los datos

Asegúrate de tener el archivo:

* data/BASERETAIL.csv

### 5. Ejecutar el pipeline de datos (ETL + RFM)
```
python main.py
```

Esto debería generar:

* data/processed/clientes_limpios.csv

* data/processed/metricas_clientes_ml.csv

### 6. Entrenar el modelo de segmentación
```
python train.py
```

Al finalizar, tendrás:

* Modelos en models/

* Datos segmentados y reportes en data/processed/

### 7. Levantar la API FastAPI
```
uvicorn api_segmentacion:app --reload --host 0.0.0.0 --port 8000
```

Endpoints útiles:

* Documentación interactiva:http://localhost:8000/docs

* Health check:http://localhost:8000/health

* Resumen de segmentos:http://localhost:8000/segments/summary

### 8. Ejecutar el Dashboard Streamlit
```
streamlit run dashboard_app.py
```

Por defecto se abrirá en:

* http://localhost:8501/

El dashboard intentará conectarse a la API en la URL configurada en el código:
```
API_BASE_URL = "https://api-segmentacion-560041103472.us-central1.run.app"
```

Para desarrollo local puedes cambiar esa URL a:
```
API_BASE_URL = "http://localhost:8000"
```

## 📌 Actividades cubiertas
El proyecto implementa todas las actividades planteadas en el caso:

1. **Pipeline:**

   * Descarga/uso del dataset especificado (Online Retail II → BASERETAIL).
   * Limpieza de datos:
     * Manejo de facturas de devolución.
     * Manejo de valores nulos en CustomerID.
   * Ingeniería de características:
     * Cálculo de métricas RFM (Recency, Frequency, Monetary) por cliente.
   * Entrenamiento de modelo K-Means.
   * Guardado del modelo y de los datos con segmento asignado.

2. **API (FastAPI):**

   * Endpoint /segments/summary:
     * Devuelve resumen de características de cada segmento.
   * Endpoint /segments/classify:
     * Permite asignar un segmento a un nuevo cliente basado en sus datos RFM.

3. **Dashboard (Streamlit):**

   * Resumen de los segmentos encontrados.
   * Visualización interactiva de los clusters:
     * Gráfico de dispersión 3D en el espacio RFM.
   * Herramienta para que el gerente de cuentas ingrese datos de RFM de un cliente y obtenga su segmento. 