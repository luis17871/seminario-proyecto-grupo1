import streamlit as st
import pandas as pd
import plotly.express as px
import os

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

# CONFIGURACIÓN
st.set_page_config(
    page_title="Dashboard RFM", 
    layout="wide"                
)

# TÍTULO PRINCIPAL
st.markdown("<h1 class='animate-in'>Dashboard de Análisis RFM de Clientes</h1>", unsafe_allow_html=True)
st.markdown("<p class='animate-in'>Seminario Complexivo | UNIANDES</p>", unsafe_allow_html=True)

# RUTAS DE DATOS
# RUTAS DE DATOS
#BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#DATA_PATH_CLIENTES = os.path.join(BASE_DIR, "data", "processed", "clientes_limpios.csv")
#DATA_PATH_METRICAS = os.path.join(BASE_DIR, "data", "processed", "metricas_clientes_ml.csv")
# RUTAS DE DATOS (version para Streamlit Cloud)
DATA_PATH_CLIENTES = "https://raw.githubusercontent.com/luis17871/seminario-proyecto-grupo1/main/data/processed/clientes_limpios.csv"
DATA_PATH_METRICAS = "https://raw.githubusercontent.com/luis17871/seminario-proyecto-grupo1/main/data/processed/metricas_clientes_ml.csv"

@st.cache_data
def cargar_datos(path):
    """
    Carga un CSV y estandariza las columnas.
    - Usa `@st.cache_data` para evitar recargar datos en cada interacción.
    - Verifica que el archivo exista → evita errores silenciosos.
    - Convierte todas las columnas a minúsculas → consistencia en nombres.
    """
    if not os.path.exists(path):
        st.error(f"Archivo no encontrado: {path}")
        st.stop()
    df = pd.read_csv(path)
    df.columns = df.columns.str.lower()  # Normaliza nombres de columnas
    return df

# Carga los datasets procesados
clientes_df = cargar_datos(DATA_PATH_CLIENTES)   # Ventas + clientes
metricas_df = cargar_datos(DATA_PATH_METRICAS)   # Métricas RFM calculadas

# FUNCIÓN PARA LIMPIAR GRÁFICOS
def limpiar_grafico(fig):
    """
    Aplica tema oscuro coherente con el dashboard.
    - Usa `plotly_dark` para consistencia visual.
    - Fondos transparentes → se integran al fondo del dashboard.
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

# PESTAÑAS
tab1, tab2 = st.tabs(["Análisis Exploratorio (EDA)", "Análisis RFM (Métricas)"])
# Dos pestañas principales para separar análisis exploratorio y segmentación

# PESTAÑA 1: EDA
with tab1:
    st.markdown("<h2 class='animate-in'>Análisis Exploratorio de Ventas y Clientes</h2>", unsafe_allow_html=True)

    # FILTROS
    col_filtro1, col_filtro2 = st.columns(2)
    with col_filtro1:
        # Países únicos
        paises = sorted(clientes_df["country"].dropna().unique())
        paises_sel = st.multiselect("Selecciona país(es):", options=paises, default=paises[:3])
        # Default: primeros 3 países

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
    st.markdown("<h3 class='animate-in'>Indicadores Clave de Desempeño (KPIs)</h3>", unsafe_allow_html=True)

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

    # EVOLUCIÓN DE VENTAS
    clientes_filtrados["mes"] = clientes_filtrados["invoice_date"].dt.to_period("M").astype(str)
    ventas_mes = clientes_filtrados.groupby("mes")["totalsum"].sum().reset_index()

    fig_ventas = px.area(
        ventas_mes, x="mes", y="totalsum",
        title="Evolución de Ventas Mensuales",
        labels={"mes": "Mes", "totalsum": "Ventas ($)"},
        color_discrete_sequence=["#34d399"]
    )
    fig_ventas = limpiar_grafico(fig_ventas)
    fig_ventas.update_traces(hovertemplate='<b>Mes:</b> %{x}<br><b>Ventas:</b> $%{y:,.0f}')
    st.plotly_chart(fig_ventas, use_container_width=True)
    # Gráfico de área para mostrar tendencia temporal

    st.markdown("---")

    # TOP 10 PRODUCTOS
    st.markdown("<h3 class='animate-in'>Productos Más Vendidos</h3>", unsafe_allow_html=True)
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

    # VENTAS POR PAÍS
    st.markdown("<h3 class='animate-in'>Ventas por País</h3>", unsafe_allow_html=True)
    ventas_pais = clientes_filtrados.groupby("country")["totalsum"].sum().reset_index().sort_values(by="totalsum", ascending=False)

    fig_paises = px.bar(
        ventas_pais.head(15),
        x="country", y="totalsum",
        labels={"country": "País", "totalsum": "Ventas ($)"},
        color="totalsum",
        color_continuous_scale="Blues"
    )
    fig_paises = limpiar_grafico(fig_paises)
    st.plotly_chart(fig_paises, use_container_width=True)

    st.markdown("---")

    # MAPA GEOGRÁFICO
    st.markdown("<h3 class='animate-in'>Mapa Geográfico de Ventas por País</h3>", unsafe_allow_html=True)

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
            title="Ventas Totales por País",
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

# PESTAÑA 2: RFM
with tab2:
    st.markdown("<h2 class='animate-in'>Análisis de Métricas RFM (Recency, Frequency, Monetary)</h2>", unsafe_allow_html=True)

    columnas_rfm = ["customer_id", "recency", "frequency", "monetary", "rfm_score"]
    if all(col in metricas_df.columns for col in columnas_rfm):

        col_r, col_f, col_m = st.columns(3)
        # DISTRIBUCIÓN DE RECENCY, FREQUENCY, MONETARY
        with col_r:
            fig_r = px.histogram(metricas_df, x="recency", nbins=30, marginal="box",
                                 title="Recency (R)", color_discrete_sequence=["#f87171"])
            fig_r = limpiar_grafico(fig_r)
            st.plotly_chart(fig_r, use_container_width=True)
        with col_f:
            fig_f = px.histogram(metricas_df, x="frequency", nbins=30, marginal="box",
                                 title="Frequency (F)", color_discrete_sequence=["#34d399"])
            fig_f = limpiar_grafico(fig_f)
            st.plotly_chart(fig_f, use_container_width=True)
        with col_m:
            fig_m = px.histogram(metricas_df, x="monetary", nbins=30, marginal="box",
                                 title="Monetary (M)", color_discrete_sequence=["#60a5fa"])
            fig_m = limpiar_grafico(fig_m)
            st.plotly_chart(fig_m, use_container_width=True)

        st.markdown("---")

        # MATRIZ DE CORRELACIÓN
        st.markdown("<h3 class='animate-in'>Correlación entre Métricas RFM</h3>", unsafe_allow_html=True)
        corr = metricas_df[["recency", "frequency", "monetary"]].corr()
        fig_corr = px.imshow(corr, text_auto=True, color_continuous_scale="RdBu_r")
        fig_corr = limpiar_grafico(fig_corr)
        st.plotly_chart(fig_corr, use_container_width=True)

        st.markdown("---")

        # RELACIÓN FRECUENCIA vs MONETARIO
        st.markdown("<h3 class='animate-in'>Relación entre Frecuencia y Valor Monetario</h3>", unsafe_allow_html=True)
        sample = metricas_df.sample(min(3000, len(metricas_df))) 
        fig_relacion = px.scatter(
            sample, x="frequency", y="monetary",
            size="monetary", color="rfm_score",
            hover_data=["customer_id"],
            color_continuous_scale="Viridis"
        )
        fig_relacion = limpiar_grafico(fig_relacion)
        st.plotly_chart(fig_relacion, use_container_width=True)

        st.markdown("---")

        # TOP 10 CLIENTES POR RFM SCORE
        st.markdown("<h3 class='animate-in'>Clientes con Mayor RFM Score</h3>", unsafe_allow_html=True)

        top_clientes = metricas_df.sort_values(by="rfm_score", ascending=False).head(10).copy()

        top_clientes["customer_id"] = top_clientes["customer_id"].astype(str)

        fig_top_clientes = px.bar(
        top_clientes, 
        x="rfm_score", 
        y="customer_id", 
        orientation="h",
        color="rfm_score", 
        color_continuous_scale="Teal"
        )

        fig_top_clientes = limpiar_grafico(fig_top_clientes)
        fig_top_clientes.update_layout(
            title="Top 10 Clientes con Mayor RFM Score",
            height=500,
            margin=dict(l=130, r=50, t=80, b=60),
            yaxis=dict(categoryorder="total ascending")
        )
        st.plotly_chart(fig_top_clientes, use_container_width=True)

    else:
        st.error("Faltan columnas: `recency`, `frequency`, `monetary`, `rfm_score`.")
