import streamlit as st
from pages import chat, insights
from api_client import check_health

st.set_page_config(
    page_title="Asistente Inteligente Operaciones",
    page_icon="🛵",
    layout="wide",
)

PAGES = {
    "💬 Bot Conversacional": chat,
    "📊 Reporte de Hallazgos": insights,
}

st.sidebar.title("🛵 Rappi")
st.sidebar.markdown("---")

selection = st.sidebar.radio("Herramientas", list(PAGES.keys()))

st.sidebar.markdown("---")


if check_health():
    st.sidebar.success("● Backend conectado")

else:
    st.sidebar.error("● Backend desconectado")

PAGES[selection].render()