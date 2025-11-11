import sys
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import joblib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts')
DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "metricas_clientes_ml.csv")
sys.path.insert(0, SCRIPTS_DIR)

# CARGAR ESTILOS
def local_css(file_path):
    """
    Carga un archivo CSS externo y lo inyecta en el dashboard
    - Usa `st.markdown` con `unsafe_allow_html=True` para aplicar estilos personalizados
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"Archivo no encontrado: {file_path}")
        st.stop()

# Construye la ruta correcta al archivo CSS
CSS_PATH = os.path.join(os.path.dirname(__file__), "assets", "styles.css")
local_css(CSS_PATH)  # Aplica todos los estilos desde styles.css

# CONFIGURACION
st.set_page_config(
    page_title="Dashboard RFM", 
    layout="wide"
)

# TITULO PRINCIPAL
st.markdown("<h1 class='animate-in'>Dashboard de Analisis RFM de Clientes</h1>", unsafe_allow_html=True)
st.markdown("<p class='animate-in'>Seminario Complexivo | UNIANDES</p>", unsafe_allow_html=True)

# RUTAS DE DATOS
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH_CLIENTES = os.path.join(BASE_DIR, "data", "processed", "clientes_limpios.csv")
DATA_PATH_METRICAS = os.path.join(BASE_DIR, "data", "processed", "metricas_clientes_ml.csv")

@st.cache_data
def cargar_datos(path):
    """
    Carga un CSV y estandariza las columnas.
    - Usa `@st.cache_data` para evitar recargar datos en cada interaccion.
    - Verifica que el archivo exista - evita errores silenciosos.
    - Convierte todas las columnas a minusculas - consistencia en nombres.
    """
    if not os.path.exists(path):
        st.error(f"Archivo no encontrado: {path}")
        st.stop()
    df = pd.read_csv(path)
    df.columns = df.columns.str.lower()  # Normaliza nombres de columnas
    return df

# Carga los datasets procesados
clientes_df = cargar_datos(DATA_PATH_CLIENTES)   # Ventas + clientes
metricas_df = cargar_datos(DATA_PATH_METRICAS)   # Metricas RFM calculadas

# FUNCION PARA LIMPIAR GRAFICOS
def limpiar_grafico(fig):
    """
    Aplica tema oscuro coherente con el dashboard.
    - Usa `plotly_dark` para consistencia visual.
    - Fondos transparentes - se integran al fondo del dashboard.
    - Texto blanco, rejillas suaves, hover personalizado.
    """
    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor='rgba(0,0,0,0)',   
        paper_bgcolor='rgba(0,0,0,0)',  
        font=dict(color="#e2e8f0", size=12),
        legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color="#e2e8f0")),
        hoverlabel=dict(bgcolor="#1e293b", font=dict(color="#e2e8f0")),
        margin=dict(l=40, r=40, t=60, b=40) 
    )
    
    fig.update_xaxes(
        showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.1)',
        title_font=dict(color="#e2e8f0"), tickfont=dict(color="#e2e8f0")
    )
    fig.update_yaxes(
        showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.1)',
        title_font=dict(color="#e2e8f0"), tickfont=dict(color="#e2e8f0")
    )
    return fig

@st.cache_data
def cargar_archivos(path):
    """
    Carga un archivo .joblib (Modelo o encoder).
    """
    print(f"\n[CARGA] Cargando archivo: {path}")
    return joblib.load(path)

# PESTANAS
tab1, tab2 = st.tabs(["Analisis Exploratorio (EDA)", "Analisis RFM (Metricas)"])
# Dos pestanas principales para separar analisis exploratorio y segmentacion

# PESTANA 1: EDA
with tab1:
    st.markdown("<h2 class='animate-in'>Analisis Exploratorio de Ventas y Clientes</h2>", unsafe_allow_html=True)
    st.markdown("---")

    # FILTROS
    col_filtro1, col_filtro2 = st.columns(2)
    with col_filtro1:
        # Paises unicos
        paises = sorted(clientes_df["country"].dropna().unique())
        paises_sel = st.multiselect("Selecciona pais(es):", options=paises, default=paises[:3])
        # Default: primeros 3 paises

    with col_filtro2:
        # Convertir fecha a datetime
        clientes_df["invoice_date"] = pd.to_datetime(clientes_df["invoice_date"], errors="coerce")
        clientes_df = clientes_df.dropna(subset=["invoice_date"])
        min_date = clientes_df["invoice_date"].min().date()
        max_date = clientes_df["invoice_date"].max().date()
        rango_fechas = st.slider("Rango de fechas:", min_value=min_date, max_value=max_date, value=(min_date, max_date))

    # APLICAR FILTROS
    clientes_filtrados = clientes_df.copy()
    if paises_sel:
        clientes_filtrados = clientes_filtrados[clientes_filtrados["country"].isin(paises_sel)]
    if rango_fechas:
        ini, fin = pd.to_datetime(rango_fechas[0]), pd.to_datetime(rango_fechas[1])
        clientes_filtrados = clientes_filtrados[
            (clientes_filtrados["invoice_date"] >= ini) & (clientes_filtrados["invoice_date"] <= fin)
        ]

    # KPIs (Indicadores Clave) 
    st.markdown("<h3 class='animate-in'>Indicadores Clave de Desempeno (KPIs)</h3>", unsafe_allow_html=True)

    total_ventas = clientes_filtrados["totalsum"].sum()
    total_transacciones = clientes_filtrados["invoice_number"].nunique()
    total_clientes = clientes_filtrados["customer_id"].nunique()
    total_productos = clientes_filtrados["product_code"].nunique()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card animate-in">
            <h3 style="margin:0; color:#10b981;">${total_ventas:,.0f}</h3>
            <p style="margin:0; color:#94a3b8; font-size:0.9rem;">Ventas Totales</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card animate-in">
            <h3 style="margin:0; color:#3b82f6;">{total_transacciones:,}</h3>
            <p style="margin:0; color:#94a3b8; font-size:0.9rem;">Facturas</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card animate-in">
            <h3 style="margin:0; color:#f59e0b;">{total_clientes:,}</h3>
            <p style="margin:0; color:#94a3b8; font-size:0.9rem;">Clientes</p>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card animate-in">
            <h3 style="margin:0; color:#ec4899;">{total_productos:,}</h3>
            <p style="margin:0; color:#94a3b8; font-size:0.9rem;">Productos</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # EVOLUCION DE VENTAS
    clientes_filtrados["mes"] = clientes_filtrados["invoice_date"].dt.to_period("M").astype(str)
    ventas_mes = clientes_filtrados.groupby("mes")["totalsum"].sum().reset_index()

    fig_ventas = px.area(
        ventas_mes, x="mes", y="totalsum",
        title="Evolucion de Ventas Mensuales",
        labels={"mes": "Mes", "totalsum": "Ventas ($)"},
        color_discrete_sequence=["#34d399"]
    )
    fig_ventas = limpiar_grafico(fig_ventas)
    fig_ventas.update_traces(hovertemplate='<b>Mes:</b> %{x}<br><b>Ventas:</b> $%{y:,.0f}')
    st.plotly_chart(fig_ventas, use_container_width=True)
    # Grafico de area para mostrar tendencia temporal

    st.markdown("---")

    # TOP 10 PRODUCTOS
    st.markdown("<h3 class='animate-in'>Productos Mas Vendidos</h3>", unsafe_allow_html=True)
    top_productos = (
        clientes_filtrados.groupby("product_description")["product_quantity"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    fig_top_prod = px.bar(
        top_productos, y="product_description", x="product_quantity",
        orientation="h", color="product_quantity",
        color_continuous_scale="emrld",
        title="Top 10",
        labels={"product_description": "Producto", "product_quantity": "Cantidad Vendida"}
    )
    fig_top_prod = limpiar_grafico(fig_top_prod)
    st.plotly_chart(fig_top_prod, use_container_width=True)

    st.markdown("---")

    # VENTAS POR PAIS
    st.markdown("<h3 class='animate-in'>Ventas por Pais</h3>", unsafe_allow_html=True)
    ventas_pais = clientes_filtrados.groupby("country")["totalsum"].sum().reset_index().sort_values(by="totalsum", ascending=False)

    fig_paises = px.bar(
        ventas_pais.head(15),
        x="country", y="totalsum",
        labels={"country": "Pais", "totalsum": "Ventas ($)"},
        color="totalsum",
        color_continuous_scale="Blues"
    )
    fig_paises = limpiar_grafico(fig_paises)
    st.plotly_chart(fig_paises, use_container_width=True)

    st.markdown("---")

    # MAPA GEOGRAFICO
    st.markdown("<h3 class='animate-in'>Mapa Geografico de Ventas por Pais</h3>", unsafe_allow_html=True)

    country_iso = {
        "United Kingdom": "GBR", "Germany": "DEU", "France": "FRA", "EIRE": "IRL",
        "Spain": "ESP", "Netherlands": "NLD", "Belgium": "BEL", "Switzerland": "CHE",
        "Portugal": "PRT", "Australia": "AUS", "Italy": "ITA", "USA": "USA"
    }
    ventas_pais_map = ventas_pais.copy()
    ventas_pais_map["iso_alpha"] = ventas_pais_map["country"].map(country_iso)
    ventas_pais_map = ventas_pais_map.dropna(subset=["iso_alpha"])

    if not ventas_pais_map.empty:
        fig_mapa = px.choropleth(
            ventas_pais_map,
            locations="iso_alpha",
            locationmode="ISO-3",
            color="totalsum",
            hover_name="country",
            color_continuous_scale="emrld",
            title="Ventas Totales por Pais",
            labels={"totalsum": "Ventas ($)"}
        )
        fig_mapa = limpiar_grafico(fig_mapa)
        fig_mapa.update_geos(
            bgcolor='rgba(0,0,0,0)',
            showland=True, landcolor="#1e293b",
            showocean=True, oceancolor="#0f172a"
        )
        st.plotly_chart(fig_mapa, use_container_width=True)
        
       
    else:
        st.warning("No hay datos para mostrar en el mapa.")

# PESTANA 2: RFM + API DE SEGMENTACION
with tab2:
    st.markdown("<h2 class='animate-in'>Analisis de Metricas RFM y Segmentacion de Clientes</h2>", unsafe_allow_html=True)
    
    # SECCION DE ENTRENAMIENTO DEL MODELO
    st.markdown("---")
    st.markdown("<h3 class='animate-in'>Entrenamiento del Modelo de Clustering</h3>", unsafe_allow_html=True)
    st.markdown("Entrena el modelo K-Means para generar segmentaciones actualizadas de clientes basadas en metricas RFM.")
    
    col_train1, col_train2, col_train3 = st.columns([2, 1, 2])
    
    with col_train2:
        ejecutar_clustering = st.button("ENTRENAR MODELO K-MEANS", type="primary", use_container_width=True)
    
    if ejecutar_clustering:
        # Crear un contenedor centrado para los mensajes
        col_msg1, col_msg2, col_msg3 = st.columns([1, 3, 1])
        
        with col_msg2:
            status_container = st.empty()
            progress_bar = st.progress(0)
        
        try:
            # Importar funciones del pipeline de entrenamiento
            import sys
            SCRIPTS_DIR = os.path.join(BASE_DIR, 'scripts')
            if SCRIPTS_DIR not in sys.path:
                sys.path.insert(0, SCRIPTS_DIR)
            
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
            
            # Configuracion
            RANDOM_STATE = 42
            N_INIT = 10
            MAX_ITER = 300
            K_MIN = 2
            K_MAX = 11
            
            # Paso 1: Cargar datos
            with col_msg2:
                status_container.info("[1/7] Cargando datos de metricas RFM...")
                progress_bar.progress(5)
            
            ruta_datos_ml = os.path.join(BASE_DIR, "data", "processed", "metricas_clientes_ml.csv")
            if not os.path.exists(ruta_datos_ml):
                with col_msg2:
                    status_container.error("Archivo de metricas RFM no encontrado. Ejecuta primero el Pipeline en Tab 1.")
            else:
                df_ml = pd.read_csv(ruta_datos_ml)
                
                with col_msg2:
                    status_container.success(f"[1/7] Datos cargados: {len(df_ml):,} clientes")
                    progress_bar.progress(10)
                
                # Paso 2: Preprocesamiento
                with col_msg2:
                    status_container.info("[2/7] Preparando features para clustering...")
                    progress_bar.progress(20)
                
                features_df, customer_ids = preparar_features_clustering(df_ml)
                feature_names = features_df.columns.tolist()
                
                with col_msg2:
                    status_container.success(f"[2/7] Features preparadas: {len(feature_names)} variables")
                    progress_bar.progress(30)
                
                # Paso 3: Normalizacion
                with col_msg2:
                    status_container.info("[3/7] Normalizando features con StandardScaler...")
                    progress_bar.progress(35)
                
                features_scaled, scaler, features_scaled_df = normalizar_features(features_df)
                
                with col_msg2:
                    status_container.success("[3/7] Features normalizadas correctamente")
                    progress_bar.progress(40)
                
                # Paso 4: Analisis de K optimo
                with col_msg2:
                    status_container.info("[4/7] Analizando numero optimo de clusters (K)...")
                    progress_bar.progress(45)
                
                analisis_k = analizar_numero_optimo_clusters(
                    features_scaled,
                    k_min=K_MIN,
                    k_max=K_MAX,
                    random_state=RANDOM_STATE
                )
                
                n_clusters = analisis_k['optimal_k_silhouette']
                
                with col_msg2:
                    status_container.success(f"[4/7] K optimo determinado: {n_clusters} clusters")
                    progress_bar.progress(55)
                
                # Paso 5: Entrenamiento del modelo
                with col_msg2:
                    status_container.info(f"[5/7] Entrenando modelo K-Means con {n_clusters} clusters...")
                    progress_bar.progress(60)
                
                kmeans, metricas = entrenar_kmeans(
                    features_scaled,
                    n_clusters=n_clusters,
                    random_state=RANDOM_STATE,
                    n_init=N_INIT,
                    max_iter=MAX_ITER
                )
                
                with col_msg2:
                    status_container.success(f"[5/7] Modelo entrenado (Silhouette: {metricas['silhouette_score']:.4f})")
                    progress_bar.progress(70)
                
                # Paso 6: Asignacion de clusters e interpretacion
                with col_msg2:
                    status_container.info("[6/7] Asignando clusters e interpretando segmentos...")
                    progress_bar.progress(75)
                
                df_completo = df_ml.copy()
                df_con_clusters = asignar_clusters_a_dataframe(
                    df_completo,
                    kmeans.labels_,
                    nombre_columna='segment'
                )
                
                interpretaciones = generar_interpretaciones_todos_clusters(
                    df_con_clusters,
                    feature_names,
                    n_clusters
                )
                
                pca, features_pca = crear_pca_visualizacion(features_scaled, n_components=2)
                
                with col_msg2:
                    status_container.success(f"[6/7] Segmentos interpretados y PCA creado")
                    progress_bar.progress(85)
                
                # Paso 7: Guardado de modelos y resultados
                with col_msg2:
                    status_container.info("[7/7] Guardando modelos y generando reportes...")
                    progress_bar.progress(90)
                
                directorio_modelos = os.path.join(BASE_DIR, 'models')
                directorio_datos = os.path.join(BASE_DIR, 'data', 'processed')
                
                rutas_modelos = guardar_modelos_clustering(kmeans, scaler, pca, n_clusters, directorio_modelos)
                ruta_csv = exportar_datos_segmentados(df_con_clusters, n_clusters, directorio_datos)
                ruta_resumen_csv = generar_resumen_ejecutivo_csv(interpretaciones, n_clusters, directorio_datos, df_con_clusters)
                ruta_acciones = generar_acciones_comerciales_por_cluster(df_con_clusters, interpretaciones, n_clusters, directorio_datos)
                
                with col_msg2:
                    progress_bar.progress(100)
                    status_container.success("MODELO ENTRENADO Y GUARDADO CON EXITO")
                
                # Mostrar resultados
                st.markdown("---")
                col_titulo1, col_titulo2, col_titulo3 = st.columns([1, 3, 1])
                with col_titulo2:
                    st.markdown("### Resultados del Entrenamiento")
                
                col_m1, col_m2, col_m3, col_m4 = st.columns(4)
                with col_m1:
                    st.metric("Clusters", n_clusters)
                with col_m2:
                    st.metric("Silhouette Score", f"{metricas['silhouette_score']:.4f}")
                with col_m3:
                    st.metric("Davies-Bouldin", f"{metricas['davies_bouldin_score']:.4f}")
                with col_m4:
                    st.metric("Clientes", f"{len(df_con_clusters):,}")
                
                st.success(f"Modelos guardados en: `{directorio_modelos}/`")
                st.info(f"Datos segmentados guardados en: `{ruta_csv}`")
                
                # Boton para recargar
                col_reload1, col_reload2, col_reload3 = st.columns([2, 1, 2])
                with col_reload2:
                    if st.button("Recargar Visualizaciones", type="secondary", use_container_width=True, key="reload_clustering"):
                        st.rerun()
                    
        except Exception as e:
            with col_msg2:
                status_container.error(f"Error durante el entrenamiento: {str(e)}")
                progress_bar.progress(0)
            st.exception(e)
    
    st.markdown("---")
    
    # IMPORTAR REQUESTS PARA LLAMADAS A LA API
    import requests
    
    # CONFIGURACION DE LA API
    # las URLs 
    API_BASE_URL = "https://seminario-proyecto-grupo1-hfknpwuk8kf7wfrmdup2gk.streamlit.app"
    API_URL_SUMMARY = f"{API_BASE_URL}/segments/summary"
    API_URL_CLASSIFY = f"{API_BASE_URL}/segments/classify"

    # FUNCION PARA VERIFICAR SI LA API ESTA ACTIVA
    @st.cache_data(ttl=60)
    def verificar_api():
        """Verifica si la API esta activa"""
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    # FUNCION PARA OBTENER RESUMEN DE SEGMENTOS
    @st.cache_data(ttl=300)
    def obtener_resumen_segmentos():
        """Obtiene el resumen de todos los segmentos desde la API"""
        try:
            response = requests.get(API_URL_SUMMARY, timeout=5)
            if response.status_code == 200:
                return response.json()
            return None
        except:
            return None
    
    # FUNCION PARA CLASIFICAR UN CLIENTE
    def clasificar_cliente_api(recency, frequency, monetary):
        """Clasifica un cliente usando la API"""
        try:
            datos = {
                "recency": float(recency),
                "frequency": int(frequency),
                "monetary": float(monetary)
            }
            response = requests.post(API_URL_CLASSIFY, json=datos, timeout=5)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            st.error(f"Error al clasificar: {e}")
            return None
    
    # VERIFICAR ESTADO DE LA API
    api_activa = verificar_api()
    
    if api_activa:
        st.success("✅ API de Segmentacion Conectada")
    else:
        st.warning("⚠️ API de Segmentacion no disponible. Inicia la API con: `python api_segmentacion.py`")
    
    st.markdown("---")
    
    # SECCION 1: RESUMEN DE SEGMENTOS DESDE LA API
    if api_activa:
        st.markdown("<h3 class='animate-in'>📊 Resumen de Segmentos de Clientes</h3>", unsafe_allow_html=True)
        
        resumen = obtener_resumen_segmentos()
        
        if resumen:
            # KPIs DE SEGMENTACION
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div class="metric-card animate-in">
                    <h3 style="margin:0; color:#3b82f6;">{resumen['total_clientes']:,}</h3>
                    <p style="margin:0; color:#94a3b8; font-size:0.9rem;">Clientes Segmentados</p>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="metric-card animate-in">
                    <h3 style="margin:0; color:#10b981;">{resumen['n_segmentos']}</h3>
                    <p style="margin:0; color:#94a3b8; font-size:0.9rem;">Segmentos Identificados</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # TARJETAS DE SEGMENTOS
            for segmento in resumen['segmentos']:
                with st.expander(f"🎯 {segmento['nombre_segmento']} (Cluster {segmento['cluster_id']})", expanded=False):
                    col_info, col_stats = st.columns([1, 1])
                    
                    with col_info:
                        st.markdown(f"**Clientes:** {segmento['n_clientes']:,} ({segmento['porcentaje_total']:.1f}%)")
                        st.markdown(f"**Estrategia Comercial:**")
                        st.info(segmento['estrategia_comercial'])
                    
                    with col_stats:
                        st.markdown("**Caracteristicas Promedio:**")
                        carac = segmento['caracteristicas']
                        st.markdown(f"- 📅 Recency: {carac['recency_promedio']:.1f} dias")
                        st.markdown(f"- 🔄 Frequency: {carac['frequency_promedio']:.1f} compras")
                        st.markdown(f"- 💰 Monetary: ${carac['monetary_promedio']:,.2f}")
                        st.markdown(f"- ⭐ RFM Score: {carac['RFM_Score_promedio']:.2f}")
            
            st.markdown("---")
            
            # VISUALIZACION DE DISTRIBUCION DE SEGMENTOS
            st.markdown("<h3 class='animate-in'>Distribucion de Clientes por Segmento</h3>", unsafe_allow_html=True)
            
            # Preparar datos para graficos
            df_segmentos = pd.DataFrame([
                {
                    'segmento': s['nombre_segmento'],
                    'cluster_id': s['cluster_id'],
                    'n_clientes': s['n_clientes'],
                    'porcentaje': s['porcentaje_total'],
                    'recency': s['caracteristicas']['recency_promedio'],
                    'frequency': s['caracteristicas']['frequency_promedio'],
                    'monetary': s['caracteristicas']['monetary_promedio'],
                    'rfm_score': s['caracteristicas']['RFM_Score_promedio']
                }
                for s in resumen['segmentos']
            ])
            
            col_pie, col_bar = st.columns(2)
            
            with col_pie:
                fig_pie = px.pie(
                    df_segmentos, 
                    values='n_clientes', 
                    names='segmento',
                    title='Proporcion de Clientes por Segmento',
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig_pie = limpiar_grafico(fig_pie)
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col_bar:
                fig_bar = px.bar(
                    df_segmentos.sort_values('rfm_score', ascending=False),
                    x='segmento',
                    y='rfm_score',
                    color='segmento',
                    title='RFM Score Promedio por Segmento',
                    labels={'rfm_score': 'RFM Score', 'segmento': 'Segmento'},
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig_bar = limpiar_grafico(fig_bar)
                st.plotly_chart(fig_bar, use_container_width=True)
            
            # COMPARACION DE METRICAS RFM POR SEGMENTO
            st.markdown("<h3 class='animate-in'>Comparacion de Metricas RFM por Segmento</h3>", unsafe_allow_html=True)
            
            # Preparar datos para comparacion
            df_metricas_comparacion = pd.DataFrame()
            for segmento in resumen['segmentos']:
                carac = segmento['caracteristicas']
                df_temp = pd.DataFrame({
                    'Segmento': [segmento['nombre_segmento']] * 3,
                    'Metrica': ['Recency (dias)', 'Frequency (compras)', 'Monetary ($)'],
                    'Valor': [
                        carac['recency_promedio'],
                        carac['frequency_promedio'],
                        carac['monetary_promedio']
                    ],
                    'Valor_Normalizado': [
                        carac['recency_promedio'] / df_segmentos['recency'].max() * 100,
                        carac['frequency_promedio'] / df_segmentos['frequency'].max() * 100,
                        carac['monetary_promedio'] / df_segmentos['monetary'].max() * 100
                    ]
                })
                df_metricas_comparacion = pd.concat([df_metricas_comparacion, df_temp], ignore_index=True)
            
            col_comp1, col_comp2 = st.columns(2)
            
            with col_comp1:
                # Grafico de barras agrupadas normalizado
                fig_comparacion = px.bar(
                    df_metricas_comparacion,
                    x='Metrica',
                    y='Valor_Normalizado',
                    color='Segmento',
                    barmode='group',
                    title='Comparacion Normalizada de Metricas (% del maximo)',
                    labels={'Valor_Normalizado': 'Porcentaje del Maximo (%)', 'Metrica': ''},
                    color_discrete_sequence=px.colors.qualitative.Set3,
                    text_auto='.1f'
                )
                fig_comparacion = limpiar_grafico(fig_comparacion)
                fig_comparacion.update_traces(texttemplate='%{y:.0f}%', textposition='outside')
                fig_comparacion.update_layout(height=500)
                st.plotly_chart(fig_comparacion, use_container_width=True)
            
            with col_comp2:
                # Grafico de lineas para ver tendencias
                fig_lineas = px.line(
                    df_metricas_comparacion,
                    x='Metrica',
                    y='Valor_Normalizado',
                    color='Segmento',
                    markers=True,
                    title='Perfil de Metricas por Segmento',
                    labels={'Valor_Normalizado': 'Valor Normalizado (%)', 'Metrica': ''},
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig_lineas = limpiar_grafico(fig_lineas)
                fig_lineas.update_traces(line=dict(width=3), marker=dict(size=10))
                fig_lineas.update_layout(height=500)
                st.plotly_chart(fig_lineas, use_container_width=True)
            
            st.markdown("---")
    
    # SECCION 2: CLASIFICADOR INTERACTIVO
    if api_activa:
        st.markdown("<h3 class='animate-in'>Clasificador de Nuevos Clientes</h3>", unsafe_allow_html=True)
        st.markdown("Ingresa los datos RFM de un cliente para obtener su segmento y estrategia comercial recomendada.")
        
        col_input1, col_input2, col_input3 = st.columns(3)
        
        with col_input1:
            input_recency = st.number_input(
                "Recency (dias desde ultima compra)",
                min_value=0.0,
                max_value=1000.0,
                value=30.0,
                step=1.0,
                help="Numero de dias desde la ultima compra del cliente"
            )
        
        with col_input2:
            input_frequency = st.number_input(
                "Frequency (numero de compras)",
                min_value=1,
                max_value=10000,
                value=50,
                step=1,
                help="Numero total de compras realizadas por el cliente"
            )
        
        with col_input3:
            input_monetary = st.number_input(
                "Monetary (valor total $)",
                min_value=0.01,
                max_value=1000000.0,
                value=2000.0,
                step=100.0,
                help="Valor total en dolares de todas las compras del cliente"
            )
        
        if st.button("Clasificar Cliente", type="primary", use_container_width=True):
            with st.spinner("Clasificando cliente..."):
                resultado = clasificar_cliente_api(input_recency, input_frequency, input_monetary)
                
                if resultado:
                    st.success("Cliente Clasificado Exitosamente")
                    
                    col_res1, col_res2 = st.columns([1, 2])
                    
                    with col_res1:
                        st.markdown(f"""
                        <div class="metric-card animate-in" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                            <h2 style="margin:0; color:white;">{resultado['nombre_segmento']}</h2>
                            <p style="margin:0; color:#e2e8f0; font-size:0.9rem;">Cluster {resultado['cluster_id']}</p>
                            <h3 style="margin-top:10px; color:#fbbf24;">RFM Score: {resultado['RFM_Score']}</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.markdown("**Datos del Cliente:**")
                        st.markdown(f"- Recency: {resultado['recency']} dias")
                        st.markdown(f"- Frequency: {resultado['frequency']} compras")
                        st.markdown(f"- Monetary: ${resultado['monetary']:,.2f}")
                    
                    with col_res2:
                        st.markdown("**Estrategia Comercial Recomendada:**")
                        st.info(resultado['estrategia_comercial'])
                        
                        # Comparar con promedios del segmento
                        if resumen:
                            segmento_info = next((s for s in resumen['segmentos'] if s['cluster_id'] == resultado['cluster_id']), None)
                            if segmento_info:
                                st.markdown("**Comparacion con el Segmento:**")
                                carac = segmento_info['caracteristicas']
                                
                                diff_r = ((resultado['recency'] - carac['recency_promedio']) / carac['recency_promedio']) * 100
                                diff_f = ((resultado['frequency'] - carac['frequency_promedio']) / carac['frequency_promedio']) * 100
                                diff_m = ((resultado['monetary'] - carac['monetary_promedio']) / carac['monetary_promedio']) * 100
                                
                                st.markdown(f"- Recency: {diff_r:+.1f}% vs promedio del segmento")
                                st.markdown(f"- Frequency: {diff_f:+.1f}% vs promedio del segmento")
                                st.markdown(f"- Monetary: {diff_m:+.1f}% vs promedio del segmento")
                else:
                    st.error("Error al clasificar el cliente. Verifica que la API este funcionando correctamente.")
        
        st.markdown("---")
    
    # SECCION 3: VISUALIZACION 3D INTERACTIVA DE CLUSTERS
    st.markdown("<h3 class='animate-in'>Visualizacion 3D de Segmentos RFM</h3>", unsafe_allow_html=True)
    st.markdown("Explora los segmentos en un espacio tridimensional interactivo (Recency, Frequency, Monetary)")
    
    # Cargar datos segmentados si existe el archivo
    try:
        DATA_PATH_SEGMENTADOS = os.path.join(BASE_DIR, "data", "processed", "clientes_mayoristas_segmentados_k3.csv")
        if os.path.exists(DATA_PATH_SEGMENTADOS):
            df_segmentados_viz = pd.read_csv(DATA_PATH_SEGMENTADOS)
            
            # Agregar nombres de segmentos si tenemos info de la API
            if api_activa and resumen:
                segmento_map = {s['cluster_id']: s['nombre_segmento'] for s in resumen['segmentos']}
                df_segmentados_viz['nombre_segmento'] = df_segmentados_viz['segment'].map(segmento_map)
            else:
                df_segmentados_viz['nombre_segmento'] = 'Cluster ' + df_segmentados_viz['segment'].astype(str)
            
            # Tomar muestra para mejorar rendimiento (max 5000 clientes)
            df_sample = df_segmentados_viz.sample(min(5000, len(df_segmentados_viz)), random_state=42)
            
            # Crear grafico 3D interactivo
            fig_3d = go.Figure()
            
            # Colores para cada segmento
            colores = ['#f87171', '#34d399', '#60a5fa']
            
            for i, segmento in enumerate(sorted(df_sample['segment'].unique())):
                df_seg = df_sample[df_sample['segment'] == segmento]
                
                fig_3d.add_trace(go.Scatter3d(
                    x=df_seg['recency'],
                    y=df_seg['frequency'],
                    z=df_seg['monetary'],
                    mode='markers',
                    name=df_seg['nombre_segmento'].iloc[0],
                    marker=dict(
                        size=4,
                        color=colores[i % len(colores)],
                        opacity=0.7,
                        line=dict(width=0)
                    ),
                    text=[f"Cliente: {cid}<br>Recency: {r:.0f}<br>Frequency: {f:.0f}<br>Monetary: ${m:,.2f}<br>RFM Score: {rfm:.2f}" 
                          for cid, r, f, m, rfm in zip(df_seg['customer_id'], df_seg['recency'], df_seg['frequency'], df_seg['monetary'], df_seg['RFM_Score'])],
                    hovertemplate='%{text}<extra></extra>'
                ))
            
            fig_3d.update_layout(
                title='Distribucion 3D de Clientes por Segmento',
                scene=dict(
                    xaxis_title='Recency (dias)',
                    yaxis_title='Frequency (compras)',
                    zaxis_title='Monetary ($)',
                    bgcolor='rgba(0,0,0,0)',
                    xaxis=dict(gridcolor='rgba(255,255,255,0.1)', showbackground=True, backgroundcolor='rgba(30,41,59,0.5)'),
                    yaxis=dict(gridcolor='rgba(255,255,255,0.1)', showbackground=True, backgroundcolor='rgba(30,41,59,0.5)'),
                    zaxis=dict(gridcolor='rgba(255,255,255,0.1)', showbackground=True, backgroundcolor='rgba(30,41,59,0.5)'),
                ),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e2e8f0'),
                legend=dict(
                    bgcolor='rgba(30,41,59,0.8)',
                    bordercolor='rgba(255,255,255,0.2)',
                    borderwidth=1
                ),
                height=700,
                hovermode='closest'
            )
            
            st.plotly_chart(fig_3d, use_container_width=True)
            
            # Informacion adicional
            col_info1, col_info2, col_info3 = st.columns(3)
            with col_info1:
                st.info(f"**Clientes mostrados:** {len(df_sample):,} de {len(df_segmentados_viz):,}")
            with col_info2:
                st.info(f"**Segmentos:** {df_sample['segment'].nunique()}")
            with col_info3:
                st.info(f"**RFM Score promedio:** {df_sample['RFM_Score'].mean():.2f}")
            
            st.markdown("---")
            
            # TABLA RESUMEN DETALLADA DE SEGMENTOS
            st.markdown("<h3 class='animate-in'>Tabla Resumen Detallada de Segmentos</h3>", unsafe_allow_html=True)
            
            # Crear tabla resumen con estadisticas por segmento
            tabla_resumen = []
            for segmento_id in sorted(df_segmentados_viz['segment'].unique()):
                df_seg = df_segmentados_viz[df_segmentados_viz['segment'] == segmento_id]
                
                resumen_seg = {
                    'Cluster': segmento_id,
                    'Segmento': df_seg['nombre_segmento'].iloc[0],
                    'N Clientes': len(df_seg),
                    'Porcentaje': f"{(len(df_seg) / len(df_segmentados_viz) * 100):.1f}%",
                    'Recency (Prom)': f"{df_seg['recency'].mean():.1f}",
                    'Recency (Med)': f"{df_seg['recency'].median():.1f}",
                    'Frequency (Prom)': f"{df_seg['frequency'].mean():.1f}",
                    'Frequency (Med)': f"{df_seg['frequency'].median():.1f}",
                    'Monetary (Prom)': f"${df_seg['monetary'].mean():,.2f}",
                    'Monetary (Med)': f"${df_seg['monetary'].median():,.2f}",
                    'RFM Score (Prom)': f"{df_seg['RFM_Score'].mean():.2f}",
                    'RFM Score (Med)': f"{df_seg['RFM_Score'].median():.2f}"
                }
                tabla_resumen.append(resumen_seg)
            
            df_tabla = pd.DataFrame(tabla_resumen)
            
            # Mostrar tabla con estilo
            st.dataframe(
                df_tabla,
                use_container_width=True,
                hide_index=True,
                column_config={
                    'Cluster': st.column_config.NumberColumn('Cluster', format='%d'),
                    'Segmento': st.column_config.TextColumn('Segmento', width='medium'),
                    'N Clientes': st.column_config.NumberColumn('N° Clientes', format='%d'),
                    'Porcentaje': st.column_config.TextColumn('%', width='small'),
                }
            )
            
            st.markdown("---")
            
        else:
            st.warning("No se encontraron datos segmentados. Ejecuta `python train.py` primero para generar los clusters.")
    
    except Exception as e:
        st.error(f"Error al cargar datos segmentados: {e}")

    # SECCION 4: VISUALIZACIONES BASADAS EN ARCHIVOS GENERADOS
    st.markdown("<h3 class='animate-in'>Dashboard de Segmentacion y Estrategias Comerciales</h3>", unsafe_allow_html=True)
    st.markdown("Visualizaciones basadas en los datos generados por el modelo de clustering entrenado.")
    
    # Buscar archivos generados mas recientes
    directorio_processed = os.path.join(BASE_DIR, "data", "processed")
    
    # Buscar el archivo de clientes segmentados
    archivos_segmentados = [f for f in os.listdir(directorio_processed) if f.startswith("clientes_mayoristas_segmentados_k") and f.endswith(".csv")]
    archivo_resumen = [f for f in os.listdir(directorio_processed) if f.startswith("resumen_ejecutivo_k") and f.endswith(".csv")]
    archivo_acciones = [f for f in os.listdir(directorio_processed) if f.startswith("acciones_comerciales_k") and f.endswith(".csv")]
    
    if archivos_segmentados and archivo_resumen and archivo_acciones:
        # Tomar el archivo mas reciente
        archivo_seg_reciente = sorted(archivos_segmentados)[-1]
        archivo_res_reciente = sorted(archivo_resumen)[-1]
        archivo_acc_reciente = sorted(archivo_acciones)[-1]
        
        # Cargar datos
        df_segmentados = pd.read_csv(os.path.join(directorio_processed, archivo_seg_reciente))
        df_resumen = pd.read_csv(os.path.join(directorio_processed, archivo_res_reciente))
        df_acciones = pd.read_csv(os.path.join(directorio_processed, archivo_acc_reciente))
        
        st.success(f"Datos cargados: {archivo_seg_reciente}")
        
        # GRAFICO 1: DISTRIBUCION DE CLIENTES POR SEGMENTO CON ESTRATEGIAS
        st.markdown("#### Distribucion de Clientes por Segmento y Estrategia Comercial")
        
        col_g1a, col_g1b = st.columns([1, 1])
        
        with col_g1a:
            # Grafico de pastel con cantidad de clientes
            fig_dist_segmentos = px.pie(
                df_resumen,
                names='nombre_segmento',
                values='n_clientes',
                title='Distribucion de Clientes por Segmento',
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            fig_dist_segmentos.update_traces(
                textposition='outside',
                textinfo='percent+label',
                hovertemplate='<b>%{label}</b><br>Clientes: %{value}<br>Porcentaje: %{percent}<extra></extra>'
            )
            fig_dist_segmentos.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e2e8f0', size=12),
                showlegend=True,
                height=400
            )
            st.plotly_chart(fig_dist_segmentos, use_container_width=True)
        
        with col_g1b:
            # Tabla de segmentos con estrategias
            st.markdown("**Estrategias por Segmento:**")
            for idx, row in df_resumen.iterrows():
                with st.expander(f"{row['nombre_segmento']} ({row['porcentaje_total']})", expanded=False):
                    st.markdown(f"**Clientes:** {row['n_clientes']:,}")
                    st.markdown(f"**Estrategia:**")
                    st.info(row['estrategia_comercial'])
        
        st.markdown("---")
        
        # GRAFICO 2: COMPARACION DE METRICAS RFM ENTRE SEGMENTOS
        st.markdown("#### Comparacion de Metricas RFM entre Segmentos")
        
        # Calcular promedios por segmento
        metricas_por_segmento = df_segmentados.groupby('segment').agg({
            'recency': 'mean',
            'frequency': 'mean',
            'monetary': 'mean',
            'RFM_Score': 'mean'
        }).reset_index()
        
        # Agregar nombres de segmentos
        if 'segment' in df_acciones.columns and 'nombre_segmento' in df_acciones.columns:
            segmento_nombres = df_acciones[['segment', 'nombre_segmento']].drop_duplicates()
            metricas_por_segmento = metricas_por_segmento.merge(segmento_nombres, on='segment', how='left')
        else:
            metricas_por_segmento['nombre_segmento'] = 'Cluster ' + metricas_por_segmento['segment'].astype(str)
        
        col_g2a, col_g2b = st.columns([1, 1])
        
        with col_g2a:
            # Grafico de barras agrupadas para R, F, M
            df_melted = metricas_por_segmento.melt(
                id_vars=['segment', 'nombre_segmento'],
                value_vars=['recency', 'frequency', 'monetary'],
                var_name='Metrica',
                value_name='Valor Promedio'
            )
            
            # Normalizar valores para mejor visualizacion
            from sklearn.preprocessing import MinMaxScaler
            scaler = MinMaxScaler()
            df_melted['Valor Normalizado'] = scaler.fit_transform(df_melted[['Valor Promedio']])
            
            fig_rfm_barras = px.bar(
                df_melted,
                x='nombre_segmento',
                y='Valor Normalizado',
                color='Metrica',
                barmode='group',
                title='Metricas RFM Normalizadas por Segmento',
                color_discrete_map={'recency': '#f87171', 'frequency': '#34d399', 'monetary': '#60a5fa'},
                hover_data={'Valor Promedio': ':.2f'}
            )
            fig_rfm_barras.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e2e8f0'),
                xaxis_title='Segmento',
                yaxis_title='Valor Normalizado (0-1)',
                height=400
            )
            st.plotly_chart(fig_rfm_barras, use_container_width=True)
        
        with col_g2b:
            # Grafico de radar para RFM Score
            fig_rfm_score = px.bar(
                metricas_por_segmento,
                x='nombre_segmento',
                y='RFM_Score',
                title='RFM Score Promedio por Segmento',
                color='RFM_Score',
                color_continuous_scale='Turbo',
                text='RFM_Score'
            )
            fig_rfm_score.update_traces(texttemplate='%{text:.2f}', textposition='outside')
            fig_rfm_score.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e2e8f0'),
                xaxis_title='Segmento',
                yaxis_title='RFM Score',
                height=400,
                showlegend=False
            )
            st.plotly_chart(fig_rfm_score, use_container_width=True)
        
        st.markdown("---")
        
        # GRAFICO 3: ANALISIS DE VALOR Y OPORTUNIDADES COMERCIALES
        st.markdown("#### Analisis de Valor y Oportunidades por Segmento")
        
        # Calcular valor total y potencial por segmento
        valor_por_segmento = df_segmentados.groupby('segment').agg({
            'monetary': ['sum', 'mean', 'count'],
            'frequency': 'mean',
            'recency': 'mean'
        }).reset_index()
        
        valor_por_segmento.columns = ['segment', 'valor_total', 'ticket_promedio', 'n_clientes', 'freq_promedio', 'recency_promedio']
        
        # Agregar nombres de segmentos
        if 'segment' in df_acciones.columns and 'nombre_segmento' in df_acciones.columns:
            valor_por_segmento = valor_por_segmento.merge(segmento_nombres, on='segment', how='left')
        else:
            valor_por_segmento['nombre_segmento'] = 'Cluster ' + valor_por_segmento['segment'].astype(str)
        
        # Calcular potencial (valor_total * frecuencia normalizada)
        valor_por_segmento['potencial_crecimiento'] = valor_por_segmento['valor_total'] * (valor_por_segmento['freq_promedio'] / valor_por_segmento['freq_promedio'].max())
        
        col_g3a, col_g3b = st.columns([2, 1])
        
        with col_g3a:
            # Grafico de burbujas: valor total vs ticket promedio vs numero de clientes
            fig_valor_burbujas = px.scatter(
                valor_por_segmento,
                x='ticket_promedio',
                y='valor_total',
                size='n_clientes',
                color='nombre_segmento',
                title='Valor Total vs Ticket Promedio (tamaño = N° Clientes)',
                hover_data={
                    'ticket_promedio': ':$,.2f',
                    'valor_total': ':$,.2f',
                    'n_clientes': ':,',
                    'freq_promedio': ':.1f',
                    'recency_promedio': ':.1f'
                },
                color_discrete_sequence=px.colors.qualitative.Bold,
                size_max=60
            )
            fig_valor_burbujas.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e2e8f0'),
                xaxis_title='Ticket Promedio ($)',
                yaxis_title='Valor Total ($)',
                height=450
            )
            st.plotly_chart(fig_valor_burbujas, use_container_width=True)
        
        with col_g3b:
            # Tarjetas con insights clave
            st.markdown("**Insights Clave:**")
            
            # Segmento con mayor valor
            segmento_mayor_valor = valor_por_segmento.loc[valor_por_segmento['valor_total'].idxmax()]
            st.metric(
                "Segmento + Valioso",
                segmento_mayor_valor['nombre_segmento'],
                f"${segmento_mayor_valor['valor_total']:,.0f}"
            )
            
            # Segmento con mayor ticket promedio
            segmento_mayor_ticket = valor_por_segmento.loc[valor_por_segmento['ticket_promedio'].idxmax()]
            st.metric(
                "Mayor Ticket Promedio",
                segmento_mayor_ticket['nombre_segmento'],
                f"${segmento_mayor_ticket['ticket_promedio']:,.2f}"
            )
            
            # Segmento con mas clientes
            segmento_mas_clientes = valor_por_segmento.loc[valor_por_segmento['n_clientes'].idxmax()]
            st.metric(
                "Mayor Base de Clientes",
                segmento_mas_clientes['nombre_segmento'],
                f"{segmento_mas_clientes['n_clientes']:,} clientes"
            )
            
            # Potencial de crecimiento
            segmento_potencial = valor_por_segmento.loc[valor_por_segmento['potencial_crecimiento'].idxmax()]
            st.metric(
                "Mayor Potencial",
                segmento_potencial['nombre_segmento'],
                "Alto potencial"
            )
        
        st.markdown("---")
        
    else:
        st.warning("No se encontraron archivos de segmentacion. Ejecuta el boton 'ENTRENAR MODELO K-MEANS' para generar los datos.")
        st.info("Los archivos necesarios son: `clientes_mayoristas_segmentados_k*.csv`, `resumen_ejecutivo_k*.csv`, y `acciones_comerciales_k*.csv`")
