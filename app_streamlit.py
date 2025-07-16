import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objs as go
from streamlit_autorefresh import st_autorefresh
from supabase import create_client, Client
from dotenv import load_dotenv, find_dotenv
import os
from datetime import datetime, timedelta

# Función para cargar variables de entorno de forma robusta
def load_environment_variables():
    """Carga las variables de entorno desde .env de forma segura"""
    
    # Obtener el directorio del script actual
    script_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(script_dir, '.env')
    
    # Intentar múltiples métodos para cargar el .env
    loaded = False
    
    # Método 1: Usar la ruta específica
    if os.path.exists(env_path):
        loaded = load_dotenv(dotenv_path=env_path)
    
    # Método 2: Usar find_dotenv() si el método 1 falla
    if not loaded:
        dotenv_path = find_dotenv()
        if dotenv_path:
            loaded = load_dotenv(dotenv_path)
    
    # Método 3: Buscar en el directorio actual
    if not loaded:
        current_dir_env = os.path.join(os.getcwd(), '.env')
        if os.path.exists(current_dir_env):
            loaded = load_dotenv(dotenv_path=current_dir_env)
    
    # Obtener variables
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    return url, key

def safe_insert_to_supabase(supabase, data_row):
    """
    Función segura para insertar datos en Supabase
    """
    try:
        # Convertir la fila a dictionary de forma segura
        row_dict = data_row.to_dict()
        
        # Extraer timestamp correctamente
        timestamp = row_dict.get('Datetime')
        
        # Verificar si el timestamp es válido
        if timestamp is None or pd.isna(timestamp):
            return False, f"Timestamp es None o NaN: {timestamp}"
        
        # Convertir timestamp a string ISO con zona horaria
        try:
            # Convertir a pandas datetime si no lo es ya
            if not isinstance(timestamp, pd.Timestamp):
                timestamp = pd.to_datetime(timestamp)
            
            # Asegurar que tenga zona horaria (UTC por defecto)
            if timestamp.tz is None:
                timestamp = timestamp.tz_localize('UTC')
            
            # Convertir a string ISO
            timestamp_str = timestamp.isoformat()
            
        except Exception as e:
            return False, f"Error al convertir timestamp: {str(e)}"
        
        # Preparar datos para inserción
        insert_data = {
            "ticker": "AAPL",
            "timestamp": timestamp_str,
            "open": float(row_dict.get('Open', 0)),
            "high": float(row_dict.get('High', 0)),
            "low": float(row_dict.get('Low', 0)),
            "close": float(row_dict.get('Close', 0)),
            "volume": int(row_dict.get('Volume', 0))
        }
        
        # Validar que los datos no sean 0 o None
        if all(insert_data[key] > 0 for key in ['open', 'high', 'low', 'close', 'volume']):
            # Verificar si ya existe este registro (evitar duplicados)
            existing = supabase.table("apple_stock_data")\
                .select("id")\
                .eq("timestamp", timestamp_str)\
                .execute()
            
            if len(existing.data) > 0:
                return True, "Registro ya existe (sin duplicar)"
            
            # Insertar en Supabase
            result = supabase.table("apple_stock_data").insert(insert_data).execute()
            return True, f"Inserción exitosa: {timestamp_str}"
        else:
            return False, f"Datos inválidos (valores cero): {insert_data}"
            
    except Exception as e:
        return False, f"Error en inserción: {str(e)}"

def insert_all_data_to_supabase(supabase, data):
    """
    Inserta TODOS los datos descargados en Supabase (no solo el último)
    """
    success_count = 0
    error_count = 0
    
    for index, row in data.iterrows():
        success, message = safe_insert_to_supabase(supabase, row)
        if success:
            success_count += 1
        else:
            error_count += 1
    
    return success_count, error_count

def apply_global_filters(df, date_range, time_range, price_min, price_max, volume_min, volume_max):
    """
    Aplica filtros globales al DataFrame
    """
    filtered_df = df.copy()
    
    # Filtro por rango de fechas
    if date_range:
        filtered_df = filtered_df[
            (filtered_df['timestamp'].dt.date >= date_range[0]) & 
            (filtered_df['timestamp'].dt.date <= date_range[1])
        ]
    
    # Filtro por horario
    if time_range:
        filtered_df = filtered_df[
            (filtered_df['timestamp'].dt.time >= time_range[0]) & 
            (filtered_df['timestamp'].dt.time <= time_range[1])
        ]
    
    # Filtro por precio de cierre
    if price_min is not None and price_max is not None:
        filtered_df = filtered_df[
            (filtered_df['close'] >= price_min) & 
            (filtered_df['close'] <= price_max)
        ]
    
    # Filtro por volumen
    if volume_min is not None and volume_max is not None:
        filtered_df = filtered_df[
            (filtered_df['volume'] >= volume_min) & 
            (filtered_df['volume'] <= volume_max)
        ]
    
    return filtered_df

# Cargar variables de entorno
url, key = load_environment_variables()

# Verificar que las variables no sean None
if not url or not key:
    st.error("❌ Error de configuración: Variables de entorno no encontradas")
    st.info("📝 Asegúrate de que existe un archivo .env con SUPABASE_URL y SUPABASE_KEY")
    st.stop()

# Crear conexión a Supabase
try:
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error(f"❌ Error al conectar con Supabase: {e}")
    st.stop()

# Auto refrescar cada 60 segundos
st_autorefresh(interval=60000, key="data_refresh")

# Configurar página
st.set_page_config(
    page_title="Apple Stock Live",
    page_icon="📈",
    layout="wide"
)

st.title("📊 Histórico de AAPL en Tiempo Real")

# 1) OPTIMIZACIÓN: Descargar solo los últimos 30 minutos de datos
try:
    # Reducir la cantidad de datos descargados
    data = yf.download(tickers='AAPL', period='1d', interval='1m')
    
    # Verificar que los datos no estén vacíos
    if data.empty:
        st.warning("⚠️ No se pudieron obtener datos de Yahoo Finance")
        st.stop()
    
    # CORRECCIÓN: Aplanar el MultiIndex de las columnas
    if isinstance(data.columns, pd.MultiIndex):
        # Aplanar las columnas del MultiIndex
        data.columns = [col[0] for col in data.columns]
    
    # Resetear índice para obtener Datetime como columna
    data = data.reset_index()
    
    # OPTIMIZACIÓN: Solo tomar los últimos 30 registros para procesamiento
    data = data.tail(30)
    
    # Mostrar información sobre los datos descargados
    st.success(f"✅ Descargados {len(data)} registros más recientes de Yahoo Finance")
    
except Exception as e:
    st.error(f"❌ Error al descargar datos de Yahoo Finance: {e}")
    st.stop()

# 2) OPTIMIZACIÓN: Solo insertar los últimos 3 registros más recientes
if not data.empty:
    try:
        # Tomar solo los últimos 3 registros para insertar (más rápido)
        recent_data = data.tail(3)
        
        success_count, error_count = insert_all_data_to_supabase(supabase, recent_data)
        
        if success_count > 0:
            st.success(f"✅ {success_count} registros insertados")
        
    except Exception as e:
        st.warning("⚠️ Error en inserción, continuando con visualización...")

# 3) OPTIMIZACIÓN: Consulta más eficiente - aumentar a 100 registros para mejores filtros
try:
    # Consultar más registros para tener mejor rango de filtros
    resp = supabase.table("apple_stock_data")\
        .select("timestamp, open, high, low, close, volume")\
        .order("timestamp", desc=True)\
        .limit(100)\
        .execute()
    
    rows = resp.data
    df = pd.DataFrame(rows)
    
    # Convertir timestamp de forma más eficiente
    if not df.empty and "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp", ascending=False).reset_index(drop=True)
        
except Exception as e:
    df = pd.DataFrame()

# 4) OPTIMIZACIÓN: Fallback más rápido
if df.empty:
    # Usar datos de Yahoo Finance directamente (más rápido)
    df = data.copy()
    df = df.rename(columns={
        'Datetime': 'timestamp',
        'Open': 'open',
        'High': 'high', 
        'Low': 'low',
        'Close': 'close',
        'Volume': 'volume'
    })
    df = df.sort_values("timestamp", ascending=False).reset_index(drop=True)
    st.info("📊 Mostrando datos directos de Yahoo Finance")

# ===== SECCIÓN DE FILTROS GLOBALES =====
st.markdown("---")
st.subheader("🔍 Filtros Globales")

# Crear columnas para organizar filtros
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**📅 Filtros de Tiempo**")
    
    # Filtro por fecha
    if not df.empty:
        min_date = df['timestamp'].dt.date.min()
        max_date = df['timestamp'].dt.date.max()
        
        date_range = st.date_input(
            "Rango de fechas",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            key="date_filter"
        )
        
        # Filtro por horario
        time_range = st.select_slider(
            "Rango de horas",
            options=[f"{i:02d}:00" for i in range(24)],
            value=("09:00", "23:00"),
            key="time_filter"
        )
        
        # Convertir strings de tiempo a objetos time
        time_start = datetime.strptime(time_range[0], "%H:%M").time()
        time_end = datetime.strptime(time_range[1], "%H:%M").time()
        time_range = (time_start, time_end)
    else:
        date_range = None
        time_range = None

with col2:
    st.markdown("**💰 Filtros de Precio**")
    
    if not df.empty:
        price_min_val = float(df['close'].min())
        price_max_val = float(df['close'].max())
        
        price_range = st.slider(
            "Rango de precios de cierre (USD)",
            min_value=price_min_val,
            max_value=price_max_val,
            value=(price_min_val, price_max_val),
            step=0.01,
            key="price_filter"
        )
        
        # Filtro por volatilidad (diferencia entre High y Low)
        df['volatility'] = df['high'] - df['low']
        volatility_min = float(df['volatility'].min())
        volatility_max = float(df['volatility'].max())
        
        volatility_range = st.slider(
            "Rango de volatilidad (High-Low)",
            min_value=volatility_min,
            max_value=volatility_max,
            value=(volatility_min, volatility_max),
            step=0.01,
            key="volatility_filter"
        )
    else:
        price_range = (0, 1000)
        volatility_range = (0, 100)

with col3:
    st.markdown("**📊 Filtros de Volumen**")
    
    if not df.empty:
        volume_min_val = int(df['volume'].min())
        volume_max_val = int(df['volume'].max())
        
        volume_range = st.slider(
            "Rango de volumen",
            min_value=volume_min_val,
            max_value=volume_max_val,
            value=(volume_min_val, volume_max_val),
            step=1000,
            key="volume_filter"
        )
        
        # Filtro por tendencia (comparar con precio anterior)
        trend_filter = st.selectbox(
            "Filtrar por tendencia",
            options=["Todos", "Subida", "Bajada", "Estable"],
            key="trend_filter"
        )
    else:
        volume_range = (0, 1000000)
        trend_filter = "Todos"

# Botón para limpiar filtros
if st.button("🗑️ Limpiar todos los filtros"):
    st.experimental_rerun()

# ===== APLICAR FILTROS =====
if not df.empty:
    # Aplicar filtros básicos
    filtered_df = apply_global_filters(
        df, 
        date_range if len(date_range) == 2 else None,
        time_range,
        price_range[0],
        price_range[1],
        volume_range[0],
        volume_range[1]
    )
    
    # Aplicar filtro de volatilidad
    if 'volatility' in filtered_df.columns:
        filtered_df = filtered_df[
            (filtered_df['volatility'] >= volatility_range[0]) & 
            (filtered_df['volatility'] <= volatility_range[1])
        ]
    
    # Aplicar filtro de tendencia
    if trend_filter != "Todos" and len(filtered_df) > 1:
        filtered_df = filtered_df.sort_values('timestamp').reset_index(drop=True)
        filtered_df['price_change'] = filtered_df['close'].diff()
        
        if trend_filter == "Subida":
            filtered_df = filtered_df[filtered_df['price_change'] > 0]
        elif trend_filter == "Bajada":
            filtered_df = filtered_df[filtered_df['price_change'] < 0]
        elif trend_filter == "Estable":
            filtered_df = filtered_df[filtered_df['price_change'] == 0]
    
    # Mostrar estadísticas de filtros
    st.markdown("---")
    col_stats1, col_stats2, col_stats3 = st.columns(3)
    
    with col_stats1:
        st.metric("📊 Registros originales", len(df))
    with col_stats2:
        st.metric("🔍 Registros filtrados", len(filtered_df))
    with col_stats3:
        percentage = (len(filtered_df) / len(df)) * 100 if len(df) > 0 else 0
        st.metric("📈 Porcentaje mostrado", f"{percentage:.1f}%")
    
    # Usar datos filtrados para el resto de la aplicación
    display_df = filtered_df.sort_values("timestamp", ascending=False).reset_index(drop=True)
else:
    display_df = df

st.markdown("---")

# 5) CORRECCIÓN: Mostrar tabla filtrada
st.subheader(f"📋 Datos Filtrados ({len(display_df)} registros)")

if not display_df.empty:
    # Mostrar tabla con columnas adicionales calculadas
    table_df = display_df.copy()
    if 'volatility' in table_df.columns:
        table_df['volatility'] = table_df['volatility'].round(2)
    
    st.dataframe(table_df, use_container_width=True)
    
    # 6) Métricas rápidas y visualizaciones con datos filtrados
    required_cols = ["open", "close", "high", "low", "volume"]
    if all(col in display_df.columns for col in required_cols):
        # Tomar el primer registro (más reciente de los filtrados)
        ultimo = display_df.iloc[0]
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("📈 Open", f"{float(ultimo['open']):.2f} USD")
        c2.metric("📉 Close", f"{float(ultimo['close']):.2f} USD")
        c3.metric("🔺 High", f"{float(ultimo['high']):.2f} USD")
        c4.metric("🔻 Low", f"{float(ultimo['low']):.2f} USD")
        c5.metric("📊 Volume", f"{int(ultimo['volume']):,}")

        st.markdown("---")

        # 7) Para las gráficas, reordenar cronológicamente (más antiguo primero)
        df_for_charts = display_df.sort_values("timestamp", ascending=True).copy()
        
        # Gráfica de línea de Close con datos filtrados
        st.subheader("📈 Precio Close - Datos Filtrados")
        fig_line = go.Figure(go.Scatter(
            x=df_for_charts["timestamp"],
            y=df_for_charts["close"],
            mode="lines+markers",
            name="Close",
            line=dict(width=3, color="#00ff88")
        ))
        fig_line.update_layout(
            xaxis_title="Hora",
            yaxis_title="Precio USD",
            template="plotly_dark",
            height=500
        )
        st.plotly_chart(fig_line, use_container_width=True)

        # 8) Candlestick con datos filtrados
        with st.expander("📊 Ver Gráfica Candlestick - Datos Filtrados"):
            fig_candle = go.Figure(data=[go.Candlestick(
                x=df_for_charts["timestamp"],
                open=df_for_charts["open"],
                high=df_for_charts["high"],
                low=df_for_charts["low"],
                close=df_for_charts["close"]
            )])
            fig_candle.update_layout(
                title="Precio de Apple (AAPL) - Datos Filtrados",
                xaxis_title="Hora",
                yaxis_title="Precio USD",
                xaxis_rangeslider_visible=True,
                template="plotly_dark",
                height=500
            )
            st.plotly_chart(fig_candle, use_container_width=True)

        st.markdown("---")

        # 9) Volumen por hora con datos filtrados
        st.subheader("📊 Volumen Acumulado por Hora - Datos Filtrados")
        df_for_charts["hora"] = df_for_charts["timestamp"].dt.strftime("%H:%M")
        vol_hora = df_for_charts.groupby("hora")["volume"].sum().reset_index()
        vol_hora = vol_hora.sort_values("hora")
        
        fig_vol = go.Figure(go.Bar(
            x=vol_hora["hora"],
            y=vol_hora["volume"],
            name="Volumen",
            marker_color="#ff6b6b"
        ))
        fig_vol.update_layout(
            title="Volumen de Transacciones por Hora",
            xaxis_title="Hora",
            yaxis_title="Volumen",
            template="plotly_white",
            height=400
        )
        st.plotly_chart(fig_vol, use_container_width=True)

        st.markdown("---")

        # 10) Gráfica de volatilidad
        if 'volatility' in df_for_charts.columns:
            st.subheader("📊 Volatilidad (High-Low) - Datos Filtrados")
            fig_volatility = go.Figure(go.Scatter(
                x=df_for_charts["timestamp"],
                y=df_for_charts["volatility"],
                mode="lines+markers",
                name="Volatilidad",
                line=dict(width=2, color="#ff9f43")
            ))
            fig_volatility.update_layout(
                title="Volatilidad del Precio (High - Low)",
                xaxis_title="Hora",
                yaxis_title="Volatilidad USD",
                template="plotly_white",
                height=400
            )
            st.plotly_chart(fig_volatility, use_container_width=True)

        # 11) Histograma de cierres con datos filtrados
        st.subheader("📊 Distribución de Precios de Cierre - Datos Filtrados")
        fig_hist = go.Figure(go.Histogram(
            x=df_for_charts["close"],
            nbinsx=20,
            marker_color="#4834d4"
        ))
        fig_hist.update_layout(
            title="Histograma de Precios de Cierre",
            xaxis_title="Precio USD",
            yaxis_title="Frecuencia",
            template="plotly_white",
            height=400
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    else:
        st.warning("⚠️ Datos incompletos en la base de datos.")
        st.info("📊 Columnas disponibles: " + ", ".join(display_df.columns.tolist()))
else:
    st.warning("⚠️ No hay datos que coincidan con los filtros seleccionados.")
    st.info("💡 Intenta ajustar los filtros para obtener más resultados.")