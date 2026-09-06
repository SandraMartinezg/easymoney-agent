"""Interfaz de chat para el agente de cross-selling de easyMoney."""

import base64
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agent import responder

ASSETS = Path(__file__).resolve().parent / "assets"
LOGO = ASSETS / "logo.png"
AVATARES = {
    "user": str(ASSETS / "avatar_usuario.png"),
    "assistant": str(ASSETS / "avatar_agente.png"),
}
EJEMPLOS = [
    "¿A quién llamo hoy para vender pension_plan? Dame 5",
    "Resume el cliente 1264530",
    "¿Por qué el cliente 1264530 tiene tanta probabilidad?",
    "¿Cuántos clientes del segmento TOP no tienen pension_plan?",
]

st.set_page_config(
    page_title="easyMoney · Agente de cross-selling",
    page_icon=str(LOGO),
    initial_sidebar_state="expanded",
)

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
        opacity: 0.12;
        pointer-events: none;
        z-index: 0;
    }}
    .cabecera {{
        background: linear-gradient(90deg, #4F8F2A, #7CC242);
        color: white;
        padding: 1.4rem 1.8rem;
        border-radius: 14px;
        margin-bottom: 1.2rem;
    }}
    .cabecera h1 {{ color: white; margin: 0; font-size: 1.9rem; }}
    .cabecera p {{ margin: 0.3rem 0 0 0; opacity: 0.9; }}
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.image(str(LOGO), width=190)
    st.markdown("### Qué puedo hacer")
    st.markdown(
        "- Decirte **a quién llamar hoy** según la campaña vigente\n"
        "- **Resumir un cliente**: perfil, productos, grupo y propensión\n"
        "- Explicar **por qué** un cliente tiene esa probabilidad\n"
        "- Responder preguntas sobre **clientes y ventas**"
    )
    st.markdown("---")
    if st.button("Nueva conversación", use_container_width=True):
        st.session_state.historial = []
        st.session_state.chat = []
        st.rerun()
    st.caption("Datos a mayo de 2019 · Modelos del TFM easyMoney")

st.markdown(
    """
    <div class="cabecera">
        <h1>Agente de cross-selling</h1>
        <p>Pregunta en lenguaje natural sobre clientes, productos y campañas.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if "historial" not in st.session_state:
    st.session_state.historial = []
if "chat" not in st.session_state:
    st.session_state.chat = []

pregunta = st.chat_input("Escribe tu pregunta")

if not st.session_state.chat:
    with st.chat_message("assistant", avatar=AVATARES["assistant"]):
        st.markdown("Hola. Soy el asistente comercial de easyMoney. ¿Por dónde empezamos?")
    columnas = st.columns(2)
    for i, ejemplo in enumerate(EJEMPLOS):
        if columnas[i % 2].button(ejemplo, use_container_width=True):
            pregunta = ejemplo

for mensaje in st.session_state.chat:
    with st.chat_message(mensaje["rol"], avatar=AVATARES[mensaje["rol"]]):
        st.markdown(mensaje["texto"])

if pregunta:
    st.session_state.chat.append({"rol": "user", "texto": pregunta})
    with st.chat_message("user", avatar=AVATARES["user"]):
        st.markdown(pregunta)

    with st.chat_message("assistant", avatar=AVATARES["assistant"]):
        with st.spinner("Consultando datos..."):
            texto, st.session_state.historial = responder(
                pregunta, st.session_state.historial
            )
        st.markdown(texto)

    st.session_state.chat.append({"rol": "assistant", "texto": texto})
    st.rerun()