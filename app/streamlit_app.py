"""Interfaz de chat para el agente de cross-selling de easyMoney."""

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agent import responder

st.set_page_config(page_title="easyMoney · Agente de cross-selling", page_icon="💬")
st.title("Agente de cross-selling · easyMoney")
st.caption("Pregunta en lenguaje natural sobre clientes, productos y ventas.")

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