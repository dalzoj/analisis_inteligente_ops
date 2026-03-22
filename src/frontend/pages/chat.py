import configparser
import plotly.graph_objects as go
import streamlit as st
from api_client import send_question

config = configparser.ConfigParser()
config.read("config/config.cfg")

_SUGGESTIONS_START = "---SUGERENCIAS---"
_SUGGESTIONS_END   = "---FIN---"

def _parse_answer(raw_answer):
    if _SUGGESTIONS_START not in raw_answer:
        return raw_answer.strip(), []
    
    parts = raw_answer.split(_SUGGESTIONS_START, 1)
    
    main_answer = parts[0].strip()
    
    suggestions_block = parts[1].split(_SUGGESTIONS_END)[0].strip()
    
    suggestions = [
        line.lstrip("- ").strip()
        for line in suggestions_block.splitlines()
        if line.strip().startswith("-")
    ]
    
    return main_answer, suggestions


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


def _render_chart(chart):
    if not chart:
        return
    fig = go.Figure(chart)
    st.plotly_chart(fig, use_container_width=True)


def _render_suggestions(suggestions):
    
    if not suggestions:
        return
    
    st.markdown("**Análisis relacionados que podrías explorar**")
    
    cols = st.columns(len(suggestions))
    
    for i, suggestion in enumerate(suggestions):
        with cols[i]:
            if st.button(suggestion, key=f"sug_{i}_{suggestion[:20]}", use_container_width=True):
                st.session_state["pending_question"] = suggestion
                st.rerun()


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

    pending = st.session_state.pop("pending_question", None)
    question = st.chat_input("Pregunta algo, ejemplo: '¿Cuáles son las 5 zonas con mayor % Lead Penetration esta semana?'") or pending

    if question:
        history_to_send = _get_history() if mode == "history" else []

        _add_to_history("user", question)

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Analizando información..."):
                try:
                    result = send_question(question, mode, history_to_send)

                    raw_answer  = result.get("answer", "")
                    model_name = result.get("model_name", "")
                    tokens_in = result.get("tokens_in", 0)
                    tokens_out = result.get("tokens_out", 0)

                    main_answer, suggestions = _parse_answer(raw_answer)

                    st.markdown(main_answer)

                    _render_chart(result.get("chart"))
                    _render_suggestions(suggestions)


                    st.caption(
                        f"🤖 {model_name}  ·  📥 {tokens_in} tokens in  ·  📤 {tokens_out} tokens out"
                    )
                    
                    _add_to_history("assistant", main_answer)

                except Exception as error:
                    error_message = f"No se pude conectar con el backend: {error}"
                    st.error(error_message)

    if st.button("Limpiar conversación"):
        st.session_state.chat_history = []
        st.rerun()