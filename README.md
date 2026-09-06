# easymoney-agent

Agente conversacional de cross-selling para easyMoney (fintech ficticia).

Un usuario de negocio pregunta en lenguaje natural ("¿a quién llamo hoy para vender pension_plan?", "resume el cliente 15843") y un LLM con tool use decide qué herramientas Python ejecutar y redacta la respuesta.

Proyecto complementario al TFM del Máster en Data Science & AI de Nuclio Digital School. No forma parte de las tareas evaluadas.


## Problema de negocio

El TFM produce un modelo de propensión (Tarea 2), una segmentación de clientes (Tarea 3) y una estrategia de campaña con su impacto económico (Tarea 4). Pero el equipo comercial no consume esos resultados directamente: necesita al equipo de datos para traducir cada pregunta en una consulta. Este agente cierra esa distancia.

- Facilita la adopción del modelo y de la estrategia por parte de negocio.
- Reduce el tiempo de preparación por contacto.
- Da autonomía a marketing sin depender del equipo de datos.

El TFM decide qué campaña hacer (nivel estratégico); el agente ayuda a ejecutarla cada día (nivel operativo). No mejora el modelo ni sustituye la decisión humana: propone, la persona decide.


## Stack

- Python
- API de Anthropic con tool use
- Streamlit
- pandas, scikit-learn, shap


## ## 
## Herramientas del agente

| Herramienta | Qué hace | Origen |
|---|---|---|
| `consultar_datos` | Filtra y agrega sobre `df_powerbi.csv` | Tarea 1 |
| `predecir_propension` | Probabilidad de compra de un producto por cliente | Modelo de la Tarea 2 |
| `obtener_segmento` | Grupo al que pertenece un cliente | Clustering de la Tarea 3 |
| `recomendar_contactos` | Lista priorizada de clientes a contactar según la estrategia de campaña | Estrategia híbrida de la Tarea 4 |
| `explicar_prediccion` | Variables que más pesan en la predicción de un cliente | SHAP sobre el modelo de la Tarea 2 |




## Estructura del repo

```
easymoney-agent/
├── agent.py              # Bucle del agente: pregunta → LLM → herramienta → respuesta
├── app/
│   └── streamlit_app.py  # Interfaz de chat
├── tools/                # Una función por herramienta, sin dependencia del LLM
├── scripts/              # Preparación de datos (se ejecuta una vez)
├── data/                 # df_powerbi.csv (no versionado)
├── models/               # Modelos de las Tareas 2 y 3 (no versionados)
├── requirements.txt
└── .env.example
```

## Datos y modelos

No se versionan. Copiar desde el repo del TFM a `data/`:

- `df_powerbi.csv` (desde `data/processed/`): 240.773 filas y 32 columnas. Ventas mensuales 2018-2019 con datos sociodemográficos, actividad comercial y productos. Separador `;` y coma decimal. La columna `em_acount` se escribe así intencionadamente.
- `scoring_grupo_pension_plan.csv` y `scoring_grupo_em_acount.csv` (desde `data/app/`): probabilidad de compra y grupo de segmentación de cada cliente elegible, generados por la Tarea 4 a partir de los modelos de las Tareas 2 y 3.
-  `clientes.csv`: una fila por cliente con su última foto (mayo 2019). Se genera con `python scripts/preparar_clientes.py RUTA_RAW_DEL_TFM`, donde `RUTA_RAW_DEL_TFM` es la carpeta `data/raw/` del repo del TFM.
- `models/`: modelo de propensión de la Tarea 2 exportado con joblib, necesario para las explicaciones SHAP.

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