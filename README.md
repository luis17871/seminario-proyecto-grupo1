# seminario-proyecto-grupo1
Repositorio Seminario Complexivo Uniandes

**Título del Proyecto**

Segmentación de Clientes para una Empresa de Retail. 

**Miembros del Equipo**

Fernando Xavier Carrión Tabango 

Brayan Alejandro Morán Chandi	 

Luis Ernesto Caicedo Mendoza 

**Definición del Problema**

Empresa retail no tiene una segmentación adecuada de sus clientes con base al consumo de los mismos, por lo tanto, el proceso de marketing no puede ser enfocado de una manera directa y eficaz. 

**Objetivo Principal**

Construir una herramienta analítica que permita identificar y segmentar la clientela de la empresa retail  y así poder dirigir los recursos de marketing adecuadamente. 

**Responsabilidades de los Componentes de la Arquitectura**

Carga y validación: cargar CSV. 

Limpieza y transformación:  Eliminar duplicados, manejar ítems nulos, normalización de campos y transformación de tipos de datos. 

Crear ingenieria para crear RFM por cliente. 

Crear ingeniería para asignación de segmentos de acuerdo con RFM, por cliente y general. 

API: 

Exponer 3 endpoints, obteniendo primero la segmentación general de clientes, luego segmentacion por cliente y asignara un segmento a un nuevo cliente de acuerdo a sus datos. 

Posibles endpoints: consulta de segmentos. 

Dashboard: 

Crear un dashboard que permita visualizar la segmentación general de los clientes. 

Crear visualizacion interactiva de los datos, por segmentación o por cliente. 

Visualización a medida. 

Filtros para la visualización de segmentación y de clientes. 

**reas Técnica**

Crear el repositorio en GitHub (con .gitignore de Python). Responsable: Luis Caicedo. 

Redactar el archivo README.md inicial con la información de este Plan de Proyecto. 

Crear el script scripts/01_data_loader.py que cargue el dataset del proyecto usando Pandas. 

 