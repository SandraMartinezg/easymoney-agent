"""Interfaz de chat para el agente de cross-selling de easyMoney."""

import base64
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agent import responder

LOGO = Path(__file__).resolve().parent / "assets" / "logo.png"

st.set_page_config(page_title="easyMoney · Agente de cross-selling", page_icon=str(LOGO))

logo_b64 = base64.b64encode(LOGO.read_bytes()).decode()
st.markdown(
    f"""
    <style>
    .stApp::before {{
        content: "";
        position: fixed;
        left: 50%;
        top: 50%;
        transform: translate(-50%, -50%);
        width: 560px;
        height: 220px;
        background: url("data:image/png;base64,{logo_b64}") no-repeat center / contain;
        opacity: 0.15;
        pointer-events: none;
        z-index: 0;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.image(str(LOGO), width=220)
st.title("Agente de cross-selling")
st.caption("Pregunta en lenguaje natural sobre clientes, productos y campañas.")

if "historial" not in st.session_state:
    st.session_state.historial = []
if "chat" not in st.session_state:
    st.session_state.chat = []

for mensaje in st.session_state.chat:
    with st.chat_message(mensaje["rol"]):
        st.markdown(mensaje["texto"])

pregunta = st.chat_input("Escribe tu pregunta")

if pregunta:
    st.session_state.chat.append({"rol": "user", "texto": pregunta})
    with st.chat_message("user"):
        st.markdown(pregunta)

    with st.chat_message("assistant"):
        with st.spinner("Consultando datos..."):
            texto, st.session_state.historial = responder(
                pregunta, st.session_state.historial
            )
        st.markdown(texto)

    st.session_state.chat.append({"rol": "assistant", "texto": texto})