

# easymoney-agent

Agente conversacional de cross-selling para easyMoney (fintech ficticia).

Un usuario de negocio pregunta en lenguaje natural ("¿a quién llamo hoy para vender pension_plan?", "resume el cliente 1264530", "¿por qué tiene tanta probabilidad?") y un LLM con tool use decide qué herramientas Python ejecutar y redacta la respuesta.

Proyecto complementario al TFM del Máster en Data Science & AI de Nuclio Digital School. No forma parte de las tareas evaluadas.

## Problema de negocio

El TFM produce un modelo de propensión (Tarea 2), una segmentación de clientes (Tarea 3) y una estrategia de campaña con su impacto económico (Tarea 4). Pero el equipo comercial no consume esos resultados directamente: necesita al equipo de datos para traducir cada pregunta en una consulta. Este agente cierra esa distancia.

- Facilita la adopción del modelo y de la estrategia por parte de negocio.
- Reduce el tiempo de preparación por contacto.
- Da autonomía a marketing sin depender del equipo de datos.

El TFM decide qué campaña hacer (nivel estratégico); el agente ayuda a ejecutarla cada día (nivel operativo). No mejora el modelo ni sustituye la decisión humana: propone, la persona decide.

## Herramientas del agente

| Herramienta | Qué hace | Origen |
|---|---|---|
| `consultar_datos` | Filtra y agrega sobre la tabla de clientes o la de ventas | Tarea 1 |
| `predecir_propension` | Probabilidad de compra de un producto por cliente | Modelo de la Tarea 2 |
| `obtener_segmento` | Grupo al que pertenece un cliente, con perfil y acción recomendada | Clustering de la Tarea 3 |
| `recomendar_contactos` | Lista priorizada de clientes a contactar según la estrategia de campaña | Estrategia híbrida de la Tarea 4 |
| `explicar_prediccion` | Variables que más pesan en la predicción de un cliente | SHAP sobre el modelo de la Tarea 2 |

Las herramientas son funciones Python puras, sin dependencia del LLM, y se prueban de forma independiente. El LLM decide cuál usar y redacta; solo el código Python toca datos.

## Stack

- Python 3.14
- API de Anthropic con tool use (modelo `claude-sonnet-5`)
- Streamlit
- pandas, pyarrow, scikit-learn, shap

## Estructura del repo

```
easymoney-agent/
├── agent.py              # Bucle del agente: pregunta → LLM → herramienta → respuesta
├── app/
│   ├── streamlit_app.py  # Interfaz de chat
│   └── assets/           # Logo y avatares
├── .streamlit/
│   └── config.toml       # Tema con los colores corporativos
├── tools/                # Una función por herramienta, sin dependencia del LLM
├── scripts/              # Preparación de datos (se ejecuta una vez)
├── data/                 # Datos (no versionados)
├── models/               # Modelo exportado (no versionado)
├── requirements.txt
└── .env.example
```

## Datos y modelos

Se incluyen en el repo (todos por debajo de 100 MB) para que la app pueda desplegarse en Streamlit Community Cloud. Proceden del repo del TFM::

- `df_powerbi.csv` (desde `data/processed/`): 240.773 filas, una por venta 2018-2019, con datos del cliente en ese mes. Separador `;` y coma decimal. La columna `em_acount` se escribe así intencionadamente.
- `clientes.csv`: una fila por cliente (456.373) con su última foto (mayo 2019). Se genera con `python scripts/preparar_clientes.py RUTA_RAW_DEL_TFM`, donde `RUTA_RAW_DEL_TFM` es la carpeta `data/raw/` del repo del TFM.
- `clientes_grupos.csv` (desde `data/processed/`): grupo de segmentación de cada cliente.
- `scoring_grupo_pension_plan.csv` y `scoring_grupo_em_acount.csv` (desde `data/app/`): probabilidad de compra y grupo de cada cliente elegible, generados por la Tarea 4.
- `X_scoring_pension_plan.parquet` (desde `data/processed/`): matriz de variables de los clientes elegibles tal como la ve el modelo, exportada desde el notebook de la Tarea 2.
- `models/modelo_pension_plan.joblib`: Random Forest de la Tarea 2, exportado desde el notebook con `joblib.dump`. Se entrenó con scikit-learn 1.6.1 y carga con 1.9.0 mostrando un aviso de versión, que se silencia en `explicar_prediccion` tras verificar que las probabilidades recalculadas coinciden con el scoring original.

## ## Demo

La app está desplegada en Streamlit Community Cloud: https://easymoney-agent-z3fqqezy2zdp8w65slnbe3.streamlit.app

## Puesta en marcha

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # y rellenar ANTHROPIC_API_KEY
python -m streamlit run app/streamlit_app.py
```

Para probar el agente sin interfaz:

```bash
python agent.py "¿A quién llamo hoy para vender pension_plan?"
```