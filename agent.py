"""Bucle del agente: pregunta → LLM → herramientas → respuesta."""

import json
import os
import traceback

from anthropic import Anthropic
from dotenv import load_dotenv

from tools.consultar_datos import consultar_datos
from tools.explicar_prediccion import explicar_prediccion
from tools.obtener_segmento import obtener_segmento
from tools.predecir_propension import predecir_propension
from tools.recomendar_contactos import recomendar_contactos

load_dotenv()

MODELO = "claude-sonnet-5"

SYSTEM_PROMPT = """Eres el asistente de cross-selling de easyMoney, una fintech.
Ayudas al equipo comercial a decidir a quién contactar y con qué argumentos.

Dispones de herramientas que consultan datos reales. Úsalas siempre que la
pregunta requiera datos; nunca inventes cifras ni clientes.

Contexto de negocio:
- Hay modelo de propensión para dos productos: pension_plan y em_acount.
- Una venta de pension_plan deja unos 5.976 € de margen; una de em_acount, unos
  70 €. La campaña recomendada es pension_plan.
- La estrategia de campaña vigente es la híbrida: contactar a todos los
  clientes de los grupos "Clientes de nómina" y "Particulares con tarjeta", más
  el top 20% del modelo en el resto de grupos. No se contacta a "Universitarios
  inactivos" ni a "Sin producto".
- Cuando pregunten "a quién llamo" o "a quién contacto", usa
  recomendar_contactos, que aplica esa estrategia. Usa predecir_propension solo
  cuando pidan explícitamente la probabilidad de un cliente o el ranking del
  modelo sin aplicar la estrategia.
- Para resumir un cliente, combina consultar_datos sobre la tabla clientes
  (sus datos y productos), obtener_segmento (su grupo y la acción recomendada)
  y predecir_propension (su probabilidad para pension_plan).
- Cuando pregunten por qué un cliente tiene esa probabilidad, o qué argumentos
  usar en la llamada, usa explicar_prediccion: las variables con impacto
  positivo son los argumentos a favor.
- Para preguntas de tipo "qué producto se vende más", "qué segmento compra
  más" o "cuánto margen deja cada producto", usa consultar_datos con
  agregacion y agrupar_por en una sola llamada; no hagas una llamada por
  producto.
- No prometas condiciones, descuentos, beneficios fiscales ni ventajas que no
  aparezcan en los datos. Los argumentos deben basarse en el perfil del
  cliente, no en ofertas.

Sobre los datos:
- Tabla "clientes": una fila por cliente (cid), 456.373 clientes, foto a mayo
  de 2019. Columnas: age, gender, salary, region_code, entry_date,
  entry_channel, active_customer, segment, una columna 0/1 por producto
  (pension_plan, payroll, payroll_account, credit_card, debit_card, loans,
  mortgage, funds, em_acount...) y n_productos.
- Tabla "ventas": una fila por venta 2018-2019 (152.754 clientes con ventas).
  Columnas: cid, month_sale, product_desc, net_margin, más las del cliente en
  ese mes. Un cliente aparece una vez por venta.
- Valores de segment: "01 - TOP", "02 - PARTICULARES", "03 - UNIVERSITARIO".
- region_code y entry_channel son códigos; no los traduzcas a nombres ni
  interpretes su significado.
- Para "cuántos clientes tienen X" usa la tabla clientes; para "cuántas ventas
  de X" o márgenes, la tabla ventas.

Responde en español, de forma breve y orientada a la acción. Si un resultado
está truncado (n_filas mayor que los registros devueltos), indícalo.
No menciones los nombres de las herramientas al usuario; ofrece lo que puedes
hacer en lenguaje de negocio ("puedo prepararte los argumentos de la llamada").
"""

HERRAMIENTAS = [
    {
        "name": "consultar_datos",
        "description": (
            "Filtra y resume las tablas de easyMoney. La tabla 'clientes' tiene "
            "una fila por cliente con su situación actual (datos sociodemográficos, "
            "actividad, productos 0/1 y n_productos); úsala para contar clientes, "
            "describir un cliente o calcular medias por perfil. La tabla 'ventas' "
            "tiene una fila por venta 2018-2019 con margen y producto vendido; "
            "úsala para preguntas sobre ventas o márgenes. Permite filtrar por "
            "igualdad, seleccionar columnas y agregar con 'count', 'mean' o 'sum', "
            "opcionalmente agrupando por una columna (por ejemplo, ventas por "
            "producto: tabla='ventas', agregacion='count', agrupar_por='product_desc')."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "tabla": {
                    "type": "string",
                    "enum": ["clientes", "ventas"],
                    "description": "Tabla a consultar. Por defecto 'clientes'.",
                },
                "filtros": {
                    "type": "object",
                    "description": "Condiciones de igualdad columna -> valor. Ejemplo: {\"pension_plan\": 1}.",
                },
                "columnas": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Columnas a devolver o sobre las que agregar. Si se omite, todas.",
                },
                "agregacion": {
                    "type": "string",
                    "enum": ["count", "mean", "sum"],
                    "description": "Si se indica, devuelve un resumen en vez de filas.",
                },
                "agrupar_por": {
                    "type": "string",
                    "description": "Columna por la que agrupar la agregación (ej. product_desc, segment, provincia). Resultado ordenado de mayor a menor.",
                },
                "limite": {
                    "type": "integer",
                    "description": "Máximo de filas o de grupos a devolver. Por defecto 20.",
                },
            },
        },
    },
    {
        "name": "predecir_propension",
        "description": (
            "Probabilidad de que un cliente contrate un producto según el modelo "
            "de propensión. Con cliente_id devuelve solo ese cliente; sin él, "
            "devuelve el top_n de clientes elegibles (que aún no tienen el producto)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "producto": {
                    "type": "string",
                    "enum": ["pension_plan", "em_acount"],
                    "description": "Producto a predecir.",
                },
                "cliente_id": {
                    "type": "integer",
                    "description": "Identificador del cliente (cid). Omitir para obtener un ranking.",
                },
                "top_n": {
                    "type": "integer",
                    "description": "Número de clientes del ranking. Por defecto 10.",
                },
            },
            "required": ["producto"],
        },
    },
    {
        "name": "obtener_segmento",
        "description": (
            "Grupo de segmentación de un cliente, con la descripción del perfil "
            "y la acción comercial recomendada para ese grupo."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "cliente_id": {
                    "type": "integer",
                    "description": "Identificador del cliente (cid).",
                },
            },
            "required": ["cliente_id"],
        },
    },
    {
        "name": "recomendar_contactos",
        "description": (
            "Lista priorizada de clientes a contactar aplicando la estrategia de "
            "campaña vigente (grupos núcleo completos más el top del modelo en el "
            "resto). Es la herramienta para responder 'a quién llamo hoy'."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "producto": {
                    "type": "string",
                    "enum": ["pension_plan", "em_acount"],
                    "description": "Producto de la campaña. Por defecto pension_plan.",
                },
                "n": {
                    "type": "integer",
                    "description": "Número de clientes a devolver. Por defecto 20.",
                },
                "top_resto_pct": {
                    "type": "integer",
                    "description": "Porcentaje del modelo a contactar fuera del núcleo. Por defecto 20.",
                },
            },
        },
    },
    {
        "name": "explicar_prediccion",
        "description": (
            "Explica la probabilidad de un cliente para pension_plan: devuelve las "
            "variables que más pesan en su predicción, con su valor y su impacto "
            "(positivo sube la probabilidad, negativo la baja)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "cliente_id": {
                    "type": "integer",
                    "description": "Identificador del cliente (cid).",
                },
                "top_variables": {
                    "type": "integer",
                    "description": "Número de variables a devolver. Por defecto 5.",
                },
            },
            "required": ["cliente_id"],
        },
    },
]

FUNCIONES = {
    "consultar_datos": consultar_datos,
    "predecir_propension": predecir_propension,
    "obtener_segmento": obtener_segmento,
    "recomendar_contactos": recomendar_contactos,
    "explicar_prediccion": explicar_prediccion,
}

cliente = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def ejecutar_herramienta(nombre: str, argumentos: dict) -> str:
    """Ejecuta la función Python asociada y devuelve el resultado como texto."""
    try:
        resultado = FUNCIONES[nombre](**argumentos)
    except Exception as e:
        print(f"[herramienta {nombre}] {type(e).__name__}: {e}", flush=True)
        traceback.print_exc()
        resultado = {"error": str(e)}
    return json.dumps(resultado, ensure_ascii=False, default=str)


def responder(pregunta: str, historial: list | None = None) -> tuple[str, list]:
    """Responde a una pregunta ejecutando herramientas si el modelo lo pide.

    Devuelve el texto final y el historial actualizado, para poder mantener
    una conversación con varios turnos.
    """
    mensajes = list(historial or [])
    mensajes.append({"role": "user", "content": pregunta})

    while True:
        respuesta = cliente.messages.create(
            model=MODELO,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=HERRAMIENTAS,
            messages=mensajes,
        )
        mensajes.append({"role": "assistant", "content": respuesta.content})
        print(
            f"[agente] stop_reason={respuesta.stop_reason} "
            f"bloques={[b.type for b in respuesta.content]}",
            flush=True,
        )

        if respuesta.stop_reason != "tool_use":
            texto = "".join(b.text for b in respuesta.content if b.type == "text")
            if not texto:
                texto = "No he podido completar la respuesta. Vuelve a intentarlo."
            return texto, mensajes

        resultados = []
        for bloque in respuesta.content:
            if bloque.type == "tool_use":
                print(f"[agente] herramienta={bloque.name} args={bloque.input}", flush=True)
                salida = ejecutar_herramienta(bloque.name, bloque.input)
                resultados.append(
                    {"type": "tool_result", "tool_use_id": bloque.id, "content": salida}
                )
        mensajes.append({"role": "user", "content": resultados})


if __name__ == "__main__":
    import sys

    pregunta = " ".join(sys.argv[1:]) or "¿A quién llamo hoy para vender pension_plan?"
    texto, _ = responder(pregunta)
    print(texto)