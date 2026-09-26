import streamlit as st
import requests
import json
import time
from openai import OpenAI

# 1. CONFIGURACIÓN VISUAL DIRECTA
st.set_page_config(page_title="Trading IA Profesional", page_icon="📈", layout="wide")
st.title("📈 Sistema de Inteligencia Artificial para Trading Profesional")
st.subheader("Análisis de Noticias e Impacto en Índices y Acciones en Tiempo Real")

# 2. CONFIGURACIÓN DE LLAVES EN LA BARRA LATERAL
st.sidebar.header("🔑 Credenciales")
NEWS_API_KEY = st.sidebar.text_input("1. Ingresa tu NewsAPI Key", value="TU_LLAVE_NEWSAPI", type="password")
OPENAI_API_KEY = st.sidebar.text_input("2. Ingresa tu OpenAI API Key", value="TU_LLAVE_OPENAI", type="password")

st.sidebar.markdown("---")
st.sidebar.header("🤖 Configuración de Telegram")
TELEGRAM_TOKEN = st.sidebar.text_input("Telegram Bot Token", value="", type="password")
TELEGRAM_CHAT_ID = st.sidebar.text_input("Telegram Chat ID", value="", type="password")

# MAPEO COMPLETO OPTIMIZADO PARA PRE-MARKET, FED, CASA BLANCA Y TICKERS
MAPEO_BUSQUEDA = {
    "Todo el Mercado (🚨 Fed + Política + SPY)": "S&P 500 OR SPY OR Powell OR Federal Reserve OR FOMC OR White House OR US President OR Tariffs",
    "SPY / SPX (S&P 500)": "S&P 500 OR SPY OR SPX",
    "QQQ (Nasdaq 100)": "Nasdaq 100 OR QQQ OR Tech stocks",
    "DIA (Dow Jones)": "Dow Jones OR DIA ETF OR Industrial stocks",
    "IWM (Russell 2000)": "Russell 2000 OR IWM OR Small cap stocks",
    "Meta (META)": "META platforms OR Mark Zuckerberg OR Meta stock",
    "Apple (AAPL)": "Apple stock OR AAPL OR Tim Cook",
    "Nvidia (NVDA)": "Nvidia stock OR NVDA OR AI chips",
    "Tesla (TSLA)": "Tesla stock OR TSLA OR Elon Musk",
    "Microsoft (MSFT)": "Microsoft stock OR MSFT OR Azure",
    "AMD (Advanced Micro Devices)": "AMD stock OR Advanced Micro Devices",
    "Fed / Reserva Federal (🚨 ALTO IMPACTO)": "Jerome Powell OR Federal Reserve OR FOMC OR Fed Chair",
    "Casa Blanca / Eventos Políticos": "White House OR Biden OR US President OR Executive Order OR US Tariffs"
}

# 3. INTERFAZ GRÁFICA Y FILTROS
col1, col2 = st.columns(2)

with col1:
    st.write("### 🔍 Filtrar Mercado")
    activo = st.selectbox("Selecciona el activo a analizar:", list(MAPEO_BUSQUEDA.keys()))

    st.write("---")
    st.write("### 🎛️ Modos de Operación")
    ejecutar_manual = st.button("🔄 Escanear Manualmente una vez")

    st.write("💡 *Enciende esto antes de salir a la calle o ponerte a trabajar:*")
    piloto_automatico = st.checkbox("🚀 ENCENDER PILOTO AUTOMÁTICO (Escaneo continuo)")
    frecuencia = st.slider("Frecuencia de escaneo automático (en segundos):", min_value=30, max_value=300, value=60)

# 4. FUNCIONES DEL MOTOR (TELEGRAM, APIS DE NOTICIAS E IA)
def enviar_telegram(mensaje, token, chat_id):
    if not token or not chat_id: return
    url = f"https://telegram.org{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": mensaje, "parse_mode": "Markdown"}
    try: requests.post(url, json=payload)
    except: pass

def obtener_noticias_fuentes_clave(query, api_key):
    """Filtra y extrae noticias de MarketWatch, Finviz y Yahoo Finance"""
    dominios = "marketwatch.com,://yahoo.com,finviz.com"
    url = f"https://newsapi.org{query}&domains={dominios}&language=en,es&sortBy=publishedAt&pageSize=3&apiKey={api_key}"
    try:
        esponse = requests.get(url)
        datos = response.json()
        return datos.get("articles", []) if datos.get("status") == "ok" else []
    except: return []

def evaluar_teoria_sardinas(titular, descripcion, openai_key):
    """Aplica las reglas de análisis predictivo pre-market y confirmación M15"""
    if not openai_key or "TU_LLAVE" in openai_key:
        return {"impacto": "⚪ NEUTRO", "estrategia_antelacion": "Esperar", "estrategia_momento": "Monitorear M15", "detalles": "Falta configurar API Key"}

    client = OpenAI(api_key=openai_key)
    prompt_sistema = (
        "Eres un Agente de Inteligencia Artificial programado bajo los principios de trading de Yoel Sardiñas "
        "y metodologías de confirmación de tendencia en gráficos de 15 minutos (M15). Tu enfoque se basa en:\n"
        "1. No adivinar la dirección antes de un evento macro (Fed o Casa Blanca). Anticipar escenarios objetivos.\n"
        "2. Identificar zonas clave pre-market y esperar la apertura para validar volumen institucional.\n"
        "3. Gestionar el riesgo de forma estricta cuidando el capital.\n\n"
        "Analiza la noticia y responde ESTRICTAMENTE en formato JSON con la siguiente estructura exacta:\n"
        "{\n"
        " 'impacto': '🟢 ALCISTA' | '🔴 BAJISTA' | '⚪ NEUTRO' | '⚠️ ALTO IMPACTO GLOBAL',\n"
        " 'estrategia_antelacion': '(Qué hacer minutos ANTES del evento o en pre-market. Máx 12 palabras)',\n"
        " 'estrategia_momento': '(Qué regla de confirmación aplicar en el momento en velas M15. Máx 12 palabras)',\n"
        " 'detalles': '(Análisis lógico de la noticia para el SPY o la acción. Máx 15 palabras)'\n"
        "}"
    )
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": prompt_sistema}, {"role": "user", "content": f"Titular: {titular}\nDescripción: {descripcion}"}],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        return json.loads(response.choices.message.content)
    except:
        return {"impacto": "⚪ NEUTRO", "estrategia_antelacion": "Monitorear", "estrategia_momento": "Esperar confirmación M15", "detalles": "Error"}

# 5. PIPELINE DE MONITOREO Y EJECUCIÓN
if "noticias_procesadas" not in st.session_state:
    st.session_state.noticias_procesadas = set()

def ejecutar_sistema_centinela():
    query_actual = MAPEO_BUSQUEDA[activo]
    noticias = obtener_noticias_fuentes_clave(query_actual, NEWS_API_KEY)

    with col2:
        st.write(f"📊 **Estado del Centinela (Último chequeo: {time.strftime('%H:%M:%S')}):**")
        if not noticias:
            st.warning("Buscando noticias nuevas en las fuentes de Wall Street...")

        for art in noticias:
            titular = art.get("title", "")
            if not titular or titular in st.session_state.noticias_procesadas:
                continue

            fuente = art.get("source", {}).get("name", "MarketWatch/Yahoo")
            desc = art.get("description", "")

            # Pasar la noticia real por la IA
            analisis = evaluar_teoria_sardinas(titular, desc, OPENAI_API_KEY)

            # Dibujar en pantalla
            with st.container():
                st.markdown(f"#### {titular}")
                st.caption(f"📢 Fuente: {fuente}")
                c1, c2, c3 = st.columns(3)
                c1.metric("Impacto", analisis.get("impacto"))
                c2.write(f"⏳ **Antelación:** {analisis.get('estrategia_antelacion')}")
                c3.write(f"⚡ **En el Momento (M15):** {analisis.get('estrategia_momento')}")
                st.write(f"💡 *Fundamento:* {analisis.get('detalles')}")
                st.markdown("---")

            # Enviar mensaje al teléfono del trader mediante Telegram
            texto_telegram = (
                f"🚨 *CENTINELA DE MERCADO IA* 🚨\n\n"
                f"📰 *Titular:* {titular}\n"
                f"📈 *Filtro:* {activo}\n"
                f"📊 *Impacto:* {analisis.get('impacto')}\n\n"
                f"⏳ *Antelación:* {analisis.get('estrategia_antelacion')}\n"
                f"⚡ *Confirmación (M15):* {analisis.get('estrategia_momento')}\n\n"
                f"💡 *Análisis:* {analisis.get('detalles')}"
            )
            enviar_telegram(texto_telegram, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)
            st.session_state.noticias_procesadas.add(titular)

# DISPARADORES DE EJECUCIÓN
if ejecutar_manual:
    ejecutar_sistema_centinela()

if piloto_automatico:
    st.success(f"🤖 Piloto Automático Encendido. Escaneando fuentes cada {frecuencia} segundos...")
    ejecutar_sistema_centinela()
    time.sleep(frecuencia)
    st.rerun()