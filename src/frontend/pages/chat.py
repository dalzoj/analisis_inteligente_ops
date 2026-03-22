import plotly.graph_objects as go
import streamlit as st

from api_client import send_question


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

                    answer      = result.get("answer", "No answer returned.")
                    model_name  = result.get("model_name", "")
                    tokens_in   = result.get("tokens_in", 0)
                    tokens_out  = result.get("tokens_out", 0)

                    st.markdown(answer)

                    _render_chart(result.get("chart"))

                    st.caption(
                        f"🤖 {model_name}  ·  📥 {tokens_in} tokens in  ·  📤 {tokens_out} tokens out"
                    )
                    _add_to_history("assistant", answer)

                except Exception as error:
                    error_message = f"No se pude conectar con el backend: {error}"
                    st.error(error_message)

    if st.button("Limpiar conversación"):
        st.session_state.chat_history = []
        st.rerun()