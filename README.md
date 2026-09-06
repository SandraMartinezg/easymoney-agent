# easymoney-agent

Agente conversacional de cross-selling para easyMoney (fintech ficticia).

Un usuario de negocio pregunta en lenguaje natural ("¿a quién llamo hoy para vender pension_plan?", "resume el cliente 15843") y un LLM con tool use decide qué herramientas Python ejecutar y redacta la respuesta.

Proyecto complementario al TFM del Máster en Data Science & AI de Nuclio Digital School. No forma parte de las tareas evaluadas.

## Problema de negocio

El TFM produce un modelo de propensión y una segmentación de clientes, pero el equipo comercial no los consume directamente: necesita al equipo de datos para traducir cada pregunta en una consulta. Este agente cierra esa distancia.

- Facilita la adopción del modelo por parte de negocio.
- Reduce el tiempo de preparación por contacto.
- Da autonomía a marketing sin depender del equipo de datos.

No mejora el modelo ni sustituye la decisión humana: propone, la persona decide.

## Herramientas del agente

| Herramienta | Qué hace | Origen |
|---|---|---|
| `consultar_datos` | Filtra y agrega sobre `df_powerbi.csv` | Tarea 1 |
| `predecir_propension` | Probabilidad de compra de un producto por cliente | Modelo de la Tarea 2 |
| `obtener_segmento` | Segmento al que pertenece un cliente | Clustering de la Tarea 3 |
| `explicar_prediccion` | Variables que más pesan en la predicción | SHAP sobre el modelo de la Tarea 2 |

## Stack

- Python
- API de Anthropic con tool use
- Streamlit
- pandas, scikit-learn, shap

## Estructura del repo

```
easymoney-agent/
├── agent.py              # Bucle del agente: pregunta → LLM → herramienta → respuesta
├── app/
│   └── streamlit_app.py  # Interfaz de chat
├── tools/                # Una función por herramienta, sin dependencia del LLM
├── data/                 # df_powerbi.csv (no versionado)
├── models/               # Modelos de las Tareas 2 y 3 (no versionados)
├── requirements.txt
└── .env.example
```

## Datos y modelos

No se versionan. Copiar desde el repo del TFM:

- `data/df_powerbi.csv`: 240.773 filas y 32 columnas. Ventas mensuales 2018-2019 con datos sociodemográficos, actividad comercial y productos. La columna `em_acount` se escribe así intencionadamente.
- `models/`: modelo de propensión (Tarea 2) y modelo de segmentación (Tarea 3).

## Fases

- **Fase 0**: README y firma de las herramientas, sin LLM.
- **Fase 1**: `consultar_datos`, bucle del agente e interfaz Streamlit.
- **Fase 2**: `predecir_propension`, `obtener_segmento` y `explicar_prediccion`.

## Puesta en marcha

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # y rellenar ANTHROPIC_API_KEY
streamlit run app/streamlit_app.py
```