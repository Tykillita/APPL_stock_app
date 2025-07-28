# 📊 Apple Stock Live Dashboard - Real-Time Trading Insights

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Framework-Streamlit-red.svg)
![Supabase](https://img.shields.io/badge/Database-Supabase-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

Una aplicación épica de dashboard en **tiempo real** para visualizar y analizar datos históricos de acciones de Apple (AAPL) con filtros avanzados y múltiples tipos de gráficas. ¡Experimenta el trading de una nueva forma!

## 🌟 Características

### 📈 Trading en Vivo
- **Datos en Tiempo Real**: Actualización automática cada 60 segundos
- **API de Yahoo Finance**: Conexión directa con datos del mercado
- **Sincronización Automática**: Inserción inteligente en base de datos

### 🔍 Sistema de Filtros Avanzados
- **Filtros Temporales**: Rango de fechas y horarios específicos
- **Filtros de Precio**: Min/Max de precios y volatilidad
- **Filtros de Volumen**: Análisis por actividad de trading
- **Filtro de Tendencias**: Movimientos alcistas, bajistas o laterales
- **Estadísticas en Vivo**: Métricas de filtrado en tiempo real

### 📊 Visualizaciones Profesionales
- **Gráfica de Línea**: Evolución temporal del precio
- **Candlestick Chart**: Análisis técnico completo (OHLC)
- **Gráfica de Volumen**: Volumen acumulado por hora
- **Análisis de Volatilidad**: Diferencias High-Low
- **Histogramas**: Distribución de precios de cierre

### 💾 Persistencia Inteligente
- **Base de Datos Supabase**: Almacenamiento en la nube
- **Optimización de Datos**: Carga incremental de últimos registros
- **Prevención de Duplicados**: Sistema inteligente anti-duplicación
- **Fallback Automático**: Datos directos si falla la BD

## 📋 Requisitos del Sistema

- Python 3.8 o superior
- Conexión a internet estable
- Cuenta gratuita en Supabase
- Navegador moderno para visualización

## 🚀 Instalación

1. **Clona el repositorio:**
```bash
git clone https://github.com/tu-usuario/apple-stock-dashboard.git
cd apple-stock-dashboard
```

2. **Instala las dependencias:**
```bash
pip install -r requirements.txt
```

3. **Configura las variables de entorno:**
```bash
# Crea el archivo .env
SUPABASE_URL=tu_supabase_url_aqui
SUPABASE_KEY=tu_supabase_anon_key_aqui
```

4. **Configura la base de datos:**
```sql
-- Ejecuta en tu proyecto de Supabase
CREATE TABLE apple_stock_data (
  id SERIAL PRIMARY KEY,
  ticker TEXT NOT NULL DEFAULT 'AAPL',
  timestamp TIMESTAMPTZ NOT NULL,
  open DECIMAL(10,2) NOT NULL,
  high DECIMAL(10,2) NOT NULL,
  low DECIMAL(10,2) NOT NULL,
  close DECIMAL(10,2) NOT NULL,
  volume BIGINT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(timestamp)
);

CREATE INDEX idx_apple_stock_timestamp ON apple_stock_data(timestamp DESC);
```

5. **Ejecuta la aplicación:**
```bash
streamlit run app.py
```

## 🎮 Cómo Usar

### Navegación Básica
1. **Inicio**: La app se carga automáticamente con datos recientes
2. **Auto-Refresh**: Se actualiza cada 60 segundos automáticamente
3. **Filtros**: Usa la sección "🔍 Filtros Globales" para personalizar
4. **Visualización**: Scroll para ver todas las gráficas disponibles

### Tipos de Filtros Disponibles:

#### Filtros Temporales 📅:
- **Rango de Fechas**: Selecciona período específico
- **Rango de Horas**: Enfócate en horarios de trading
- **Auto-detección**: Rangos basados en datos disponibles

#### Filtros de Mercado 💰:
- **Rango de Precios**: Min/Max del precio de cierre
- **Volatilidad**: Diferencia entre High y Low
- **Slider Inteligente**: Basado en datos reales

#### Filtros de Actividad 📊:
- **Rango de Volumen**: Filtra por actividad de trading
- **Tendencias**: Solo subidas, bajadas o movimientos estables
- **Estadísticas**: Contador de registros filtrados

## 📊 Sistema de Métricas

La aplicación muestra métricas en tiempo real:

### Métricas Principales:
- 📈 **Open**: Precio de apertura
- 📉 **Close**: Precio de cierre actual
- 🔺 **High**: Precio máximo del período
- 🔻 **Low**: Precio mínimo del período
- 📊 **Volume**: Volumen de transacciones

### Estadísticas de Filtros:
- 📊 **Registros Originales**: Total de datos descargados
- 🔍 **Registros Filtrados**: Datos que pasan los filtros
- 📈 **Porcentaje Mostrado**: Eficiencia del filtrado

## 🎨 Tipos de Visualizaciones

### Gráficas Principales:

#### 📈 Gráfica de Línea
- Evolución temporal del precio de cierre
- Línea suavizada con marcadores
- Tema oscuro con color verde vibrante

#### 🕯️ Gráfica Candlestick
- Análisis técnico profesional (OHLC)
- Expandible con rango deslizable
- Ideal para análisis de patrones

#### 📊 Gráfica de Volumen por Hora
- Volumen acumulado en barras
- Agrupación automática por hora
- Color distintivo para fácil lectura

#### 📈 Análisis de Volatilidad
- Diferencia High-Low en tiempo real
- Identificación de períodos volátiles
- Línea continua con marcadores

#### 📊 Histograma de Distribución
- Distribución de precios de cierre
- 20 bins automáticos
- Útil para identificar rangos frecuentes

## 🏗️ Arquitectura del Código

### Funciones Principales:

#### `load_environment_variables()`
- Carga robusta de variables de entorno
- Múltiples métodos de búsqueda del .env
- Validación automática de credenciales

#### `safe_insert_to_supabase()`
- Inserción segura con validación
- Prevención de duplicados
- Manejo de errores detallado

#### `apply_global_filters()`
- Sistema de filtrado multi-criterio
- Aplicación eficiente con pandas
- Preservación de tipos de datos

### Optimizaciones Implementadas:
- **Carga Incremental**: Solo últimos 30 registros para procesamiento
- **Inserción Inteligente**: Solo 3 registros más recientes
- **Consulta Eficiente**: 100 registros con índices optimizados
- **Fallback Robusto**: Datos directos si falla la BD

## 📁 Estructura del Proyecto

```
apple-stock-dashboard/
│
├── app.streemlit.py      # Aplicación principal de Streamlit
├── requirements.txt      # Dependencias de Python
├── .env                  # Variables de entorno (no versionar)
├── .gitignore            # Archivos ignorados por Git
├── README.md             # Este archivo
├── LICENSE               # Licencia MIT
└── screenshots/          # Capturas de pantalla
    ├── dashboard.png
    ├── filters.png
    └── charts.png
```

## 🔧 Personalización

### Cambiar Intervalo de Actualización:
```python
# En app.streemlit.py, línea ~175
st_autorefresh(interval=30000, key="data_refresh")  # 30 segundos
```

### Modificar Cantidad de Datos:
```python
# Cambiar registros a procesar
data = data.tail(50)  # Últimos 50 en lugar de 30

# Cambiar registros a insertar  
recent_data = data.tail(5)  # Últimos 5 en lugar de 3
```

### Personalizar Colores de Gráficas:
```python
# Gráfica de línea
line=dict(width=3, color="#ff6b6b")  # Rojo en lugar de verde

# Gráfica de volumen
marker_color="#4834d4"  # Púrpura en lugar de rojo
```

### Añadir Nuevos Símbolos:
```python
# Cambiar ticker
data = yf.download(tickers='MSFT', period='1d', interval='1m')
```

## 🐛 Solución de Problemas

### Error de Variables de Entorno:
```bash
❌ Error de configuración: Variables de entorno no encontradas

# Solución:
1. Verifica que .env existe en el directorio raíz
2. Confirma el formato: SUPABASE_URL=tu_url
3. Reinicia la aplicación
```

### Error de Conexión a Supabase:
```bash
❌ Error al conectar con Supabase

# Solución:
1. Verifica las credenciales en Supabase
2. Confirma que el proyecto está activo
3. Revisa la configuración de la tabla
```

### Datos Vacíos de Yahoo Finance:
```bash
⚠️ No se pudieron obtener datos de Yahoo Finance

# Solución:
1. Verifica tu conexión a internet
2. Espera unos minutos (límites de API)
3. Reinicia la aplicación
```

### Problemas de Rendimiento:
- **Reduce** la cantidad de registros procesados
- **Aumenta** el intervalo de auto-refresh
- **Cierra** otras aplicaciones pesadas

## 📦 Dependencias (requirements.txt)

```txt
streamlit>=1.28.0
pandas>=2.0.0
yfinance>=0.2.18
plotly>=5.15.0
streamlit-autorefresh>=0.0.1
supabase>=1.0.0
python-dotenv>=1.0.0
numpy>=1.21.0
```

## 🤝 Contribuir

¡Las contribuciones son bienvenidas!

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

### Ideas para Contribuir:
- 🔔 **Sistema de Alertas**: Notificaciones por cambios de precio
- 📊 **Indicadores Técnicos**: RSI, MACD, Moving Averages
- 🌐 **Múltiples Símbolos**: Soporte para otros stocks
- 📱 **Diseño Móvil**: Optimización para dispositivos móviles
- 🤖 **Análisis Predictivo**: ML para predicciones de precio
- 📈 **Backtesting**: Simulación de estrategias de trading

## 📝 Changelog

### v1.0.0 (Actual)
- ✅ Dashboard en tiempo real funcional
- ✅ Sistema de filtros avanzados
- ✅ 5 tipos de visualizaciones
- ✅ Integración con Supabase
- ✅ Optimizaciones de rendimiento
- ✅ Manejo robusto de errores

### Próximas Versiones:
- 🔄 **v1.1.0**: Sistema de alertas por email
- 🎯 **v1.2.0**: Indicadores técnicos profesionales
- 🏅 **v1.3.0**: Soporte multi-símbolo
- 📊 **v1.4.0**: Dashboard personalizable

## 👨‍💻 Autor

**Tu Nombre**
- GitHub: [@tykillita](https://github.com/tykillita)
- LinkedIn: [rubenpino](https://www.linkedin.com/in/rubenpino/)
- Proyecto: [Apple Stock Dashboard](https://github.com/tykillita/apple-stock-dashboard)

## 🙏 Agradecimientos

- 📊 **yfinance**: Por la increíble API de datos financieros
- 🚀 **Streamlit**: Por hacer el desarrollo web tan simple
- 💾 **Supabase**: Por la base de datos en tiempo real
- 📈 **Plotly**: Por las visualizaciones interactivas profesionales
- 🐍 **Python Community**: Por las librerías de análisis de datos

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

**¿Te gustó el proyecto? ¡Dale una ⭐ en GitHub y compártelo con otros traders!**

¡Que comience el análisis en tiempo real! 🚀📈
