# Seminario-Proyecto-Grupo1

Repositorio para el Seminario Complexivo de Uniandes. Este proyecto desarrolla una herramienta de segmentación de clientes para una empresa de retail utilizando análisis RFM (Recency, Frequency, Monetary).

## Título del Proyecto
Segmentación de Clientes para una Empresa de Retail.

## Miembros del Equipo
- Fernando Xavier Carrión Tabango
- Brayan Alejandro Morán Chandi
- Luis Ernesto Caicedo Mendoza

## Definición del Problema
La empresa de retail carece de una segmentación adecuada de sus clientes basada en su consumo, lo que impide enfocar el marketing de manera directa y eficaz.

## Objetivo Principal
Construir una herramienta analítica que identifique y segmente la clientela de la empresa retail, permitiendo dirigir los recursos de marketing de forma adecuada.

## Responsabilidades de los Componentes de la Arquitectura
- **Carga y Validación**: Cargar el archivo CSV principal.
- **Limpieza y Transformación**: Eliminar duplicados, manejar valores nulos, normalizar campos y transformar tipos de datos.
- **Ingeniería de Características**: Crear métricas RFM (Recency, Frequency, Monetary) por cliente.
- **Asignación de Segmentos**: Asignar segmentos basados en RFM, tanto por cliente como de forma general.
- **API**: Exponer 3 endpoints:
  - Segmentación general de clientes.
  - Segmentación por cliente específico.
  - Asignación de segmento a un nuevo cliente basado en sus datos.
  - Posibles endpoints adicionales: Consulta de segmentos.
- **Dashboard**: 
  - Visualizar la segmentación general de clientes.
  - Crear visualizaciones interactivas por segmentación o cliente.
  - Visualizaciones personalizadas.
  - Filtros para segmentación y clientes.

## Requisitos
- Python 3.8 o superior.
- Librerías: Pandas (para carga de datos). Instalar con `pip install pandas`.
- Dataset: `BASERETAIL.csv` (colocarlo en la carpeta `data/`).

## Instalación
1. Clonar el repositorio: `git clone https://github.com/luis17871/seminario-proyecto-grupo1.git`
2. Navegar al directorio: `cd seminario-proyecto-grupo1`
3. Crear un entorno virtual (opcional pero recomendado): `python -m venv venv` y activarlo (`source venv/bin/activate` en Unix o `venv\Scripts\activate` en Windows).
4. Instalar dependencias: `pip install -r requirements.txt`.

## Uso
- Ejecutar el script de carga de datos: `python scripts/01_data_loader.py`
  - Esto carga `data/BASERETAIL.csv`, muestra las primeras 5 filas y la información del DataFrame.
- En fases futuras: Usar la API o el dashboard (por implementar).

## Áreas Técnicas Iniciales
- Crear el repositorio en GitHub con `.gitignore` para Python. Responsable: Luis Caicedo.
- Redactar el archivo `README.md` inicial con el plan de proyecto.
- Desarrollar el script `scripts/01_data_loader.py` para cargar el dataset usando Pandas.

## Arquitectura actual del Proyecto

El proyecto sigue una arquitectura modular ETL (Extracción, Transformación y Carga), organizada dentro de la carpeta `scripts/`.

| Etapa                                | Archivo                 | Descripción                                                                |
| ------------------------------------ | ----------------------- | -------------------------------------------------------------------------- |
| **1️⃣ Carga de Datos**               | `data_loader.py`        | Carga el dataset base (`BASERETAIL.csv`) y lo convierte en un DataFrame.   |
| **2️⃣ Limpieza de Datos**            | `data_cleaning.py`      | Corrige nombres, tipos, y elimina facturas canceladas o precios negativos. |
| **3️⃣ Imputación de Valores**        | `imputation.py`         | Rellena valores faltantes: promedio (numéricos) o moda (categóricos).      |
| **4️⃣ Generación de Features (RFM)** | `data_new_features.py`  | Calcula métricas RFM y segmenta clientes según reglas de negocio.          |
| **5️⃣ Guardado de Resultados**       | `data_saving.py`        | Guarda los resultados procesados en `data/processed/`.                     |

---
## 🧩 Flujo General del Proceso

Carga → Limpieza → Imputación → Generación RFM → Guardado

---
## ⚙️ Requisitos del Entorno

**Python 3.9 o superior**

Instalar dependencias:
```
pip install -r requirements.txt
```
Librerías principales:
- `pandas`
- `numpy`
- `scikit-learn`
- `matplotlib`
- `missingno`
---
## Estructura del Proyecto

```
seminario-proyecto-grupo1/ 
│
├── data/
│   ├── BASERETAIL.csv
│   └── processed/
│       └── clientes_features.csv
│
├── scripts/
│   ├── data_loader.py
│   ├── data_cleaning.py
│   ├── imputation.py
│   ├── data_new_features.py
│   ├── data_saving.py
│
├── main.py
└── README.md
```
---
## Ejecución del Proyecto
Ejecutar todo el proceso:
```
python main.py
```
Resultados esperados:

- `clientes_features.csv` → dataset final con segmentos RFM.

---
## Resultados Esperados

| Segmento       | Descripción                                     | RFM Promedio |
| -------------- | ----------------------------------------------- | ------------ |
| **VIP**        | Clientes de alto valor, frecuentes y recientes. | 11.07        |
| **Leal**       | Compran con frecuencia y estabilidad.           | 8.38         |
| **Prometedor** | Clientes con potencial de crecimiento.          | 6.87         |
| **En Riesgo**  | Han dejado de comprar recientemente.            | 4.24         |
| **Durmiente**  | Actividad mínima o antigua.                     | 3.00         |

---

## Modelado y Dashboard Interactivo

Con la evolución del proyecto, se incorporó una fase de modelado de datos y visualización interactiva, ampliando el alcance del análisis RFM hacia una segmentación automática de clientes mediante algoritmos de machine learning y una interfaz visual desarrollada en Streamlit.

Nuevos Módulos Agregados

Etapa	Archivo	Descripción

6️⃣ Preprocesamiento de Datos ML	model_preprocessing.py	Escala los datos, aplica reducción dimensional (PCA) y determina el número óptimo de clusters usando Elbow y Silhouette.

7️⃣ Entrenamiento del Modelo	model_training.py	Entrena el modelo K-Means, calcula métricas (Silhouette, Davies-Bouldin, Calinski-Harabasz) y asigna etiquetas de segmento.

8️⃣ Guardado del Modelo	model_saving.py	Guarda los modelos (KMeans, Scaler, PCA) en formato .joblib y exporta resultados segmentados a CSV.

9️⃣ Orquestador General	main.py	Ejecuta de manera secuencial todo el pipeline ETL + ML, generando los archivos finales procesados.

🔟 Dashboard Interactivo	dashboard_app.py	Implementado con Streamlit y Plotly, permite explorar clientes, ventas, métricas RFM y clusters mediante visualizaciones dinámicas.

Dashboard Streamlit

El dashboard cuenta con dos secciones principales:

Análisis Exploratorio (EDA):

Indicadores clave de ventas totales, clientes, facturas y productos.

Evolución de ventas por mes y país.

Productos más vendidos.

Mapa geográfico de ventas.

Análisis RFM:

Distribución de métricas Recency, Frequency y Monetary.

Correlaciones y relaciones entre variables RFM.

Top 10 clientes con mayor RFM Score.

Para ejecutar el dashboard:

streamlit run dashboard_app.py

