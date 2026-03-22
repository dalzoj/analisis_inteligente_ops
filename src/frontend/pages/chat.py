import os
import configparser
from datetime import datetime
import plotly.graph_objects as go
import streamlit as st
from fpdf import FPDF
from api_client import send_question

config = configparser.ConfigParser()
config.read("config/config.cfg")


def _get_history():
    return st.session_state.get("chat_history", [])


def _add_to_history(role, content):
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    st.session_state.chat_history.append({"role": role, "content": content})


def _render_history():
    for message in _get_history():
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def _render_chart(chart_data):
    if not chart_data:
        return
    fig = go.Figure(chart_data)
    st.plotly_chart(fig, use_container_width=True)


def _export_to_pdf(history):
    print('INFO: chat -> _export_to_pdf')
    
    storage_path = config["paths"]["storage"]

    os.makedirs(storage_path, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    filename  = f"conversacion_{timestamp}.pdf"
    filepath  = os.path.join(storage_path, filename)
    print(filepath)
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Conversacion - Asistente Rappi", ln=True)

    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 8, f"Exportado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.ln(4)

    for message in history:
        role    = message["role"]
        content = message["content"]

        if role == "user":
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(30, 30, 200)
            pdf.cell(0, 8, "Usuario:", ln=True)
        else:
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(0, 130, 0)
            pdf.cell(0, 8, "Asistente:", ln=True)

        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 7, content.encode("latin-1", "replace").decode("latin-1"))
        pdf.ln(3)
    
    pdf.output(filepath)
    
    with open(filepath, "rb") as f:
        pdf_bytes = f.read()
    
    return pdf_bytes, filename


def render():
    st.title("Bot Conversacional")
    st.caption("Realiza preguntas sobre las métricas operacionales y recibe respuestas precisas.")

    mode = st.radio(
        "Modo de conversación",
        options=["basic", "history"],
        format_func=lambda m: "💬 Solo esta interacción" if m == "basic" else "🧠 Conversacional (recuerda el contexto)",
        horizontal=True,
    )

    if mode == "history":
        st.info("El bot recordará las últimas interacciones para mantener el contexto de la conversación.", icon="🧠")

    st.markdown("---")

    _render_history()

    question = st.chat_input("Pregunta algo, ejemplo: '¿Cuáles son las 5 zonas con mayor % Lead Penetration esta semana?'")

    if question:
        history_to_send = _get_history() if mode == "history" else []

        _add_to_history("user", question)

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Analizando información..."):
                try:
                    result = send_question(question, mode, history_to_send)

                    answer = result.get("answer", "No answer returned.")
                    model_name = result.get("model_name", "")
                    tokens_in = result.get("tokens_in", 0)
                    tokens_out = result.get("tokens_out", 0)

                    st.markdown(answer)

                    _render_chart(result.get("chart"))

                    st.caption(
                        f"🤖 {model_name}  ·  📥 {tokens_in} tokens in  ·  📤 {tokens_out} tokens out"
                    )
                    _add_to_history("assistant", answer)

                except Exception as error:
                    error_message = f"No se pude conectar con el backend: {error}"
                    st.error(error_message)

    col_limpiar, col_exportar = st.columns([1, 1])

    with col_limpiar:
        if st.button("Limpiar conversación"):
            st.session_state.chat_history = []
            st.rerun()

    with col_exportar:
        history = _get_history()

        if history:
            try:
                pdf_bytes, filename = _export_to_pdf(history)
                st.download_button(
                    label="Exportar conversación a PDF",
                    data=pdf_bytes,
                    file_name=filename,
                    mime="application/pdf",
                )
            except Exception as error:
                st.error(f"Error al generar el PDF: {error}")
        else:
            st.button("Exportar conversación a PDF", disabled=True)