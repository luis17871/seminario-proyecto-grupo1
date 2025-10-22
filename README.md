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
4. Instalar dependencias: `pip install -r requirements.txt` (crea este archivo si no existe, agregando `pandas`).

## Uso
- Ejecuta el script de carga de datos: `python scripts/01_data_loader.py`
  - Esto carga `data/BASERETAIL.csv`, muestra las primeras 5 filas y la información del DataFrame.
- En fases futuras: Usa la API o el dashboard (por implementar).

## Áreas Técnicas Iniciales
- Crear el repositorio en GitHub con `.gitignore` para Python. Responsable: Luis Caicedo.
- Redactar el archivo `README.md` inicial con el plan de proyecto.
- Desarrollar el script `scripts/01_data_loader.py` para cargar el dataset usando Pandas.

## Estado del Proyecto
En desarrollo inicial. Próximos pasos: Implementar limpieza de datos, RFM y API.