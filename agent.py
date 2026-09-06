"""Bucle del agente: pregunta → LLM → herramientas → respuesta."""

import json
import os

from anthropic import Anthropic
from dotenv import load_dotenv

from tools.consultar_datos import consultar_datos

load_dotenv()

MODELO = "claude-sonnet-5"

SYSTEM_PROMPT = """Eres el asistente de cross-selling de easyMoney, una fintech.
Ayudas al equipo comercial a decidir a quién contactar y con qué argumentos.

Dispones de herramientas que consultan datos reales. Úsalas siempre que la
pregunta requiera datos; nunca inventes cifras ni clientes.

Sobre el dataset (df_powerbi.csv): cada fila es una venta, no un cliente, así
que un mismo cliente (columna cid) aparece una vez por producto contratado.
Columnas principales: cid, month_sale, product_desc, net_margin, age, gender,
salary, provincia, entry_channel, active_customer, segment, y una columna 0/1
por producto (pension_plan, credit_card, loans, mortgage, funds, em_acount...).
Valores de segment: "01 - TOP", "02 - PARTICULARES", "03 - UNIVERSITARIO".

Responde en español, de forma breve y orientada a la acción. Si un resultado
está truncado (n_filas mayor que los registros devueltos), indícalo.
"""

HERRAMIENTAS = [
    {
        "name": "consultar_datos",
        "description": (
            "Filtra y resume el dataset de ventas y clientes de easyMoney. "
            "Permite filtrar por igualdad en cualquier columna, seleccionar "
            "columnas, y agregar con 'count' (número de filas) o 'mean' "
            "(media de las columnas numéricas seleccionadas)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "filtros": {
                    "type": "object",
                    "description": "Condiciones de igualdad columna -> valor. Ejemplo: {\"pension_plan\": 1}.",
                },
                "columnas": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Columnas a devolver. Si se omite, todas.",
                },
                "agregacion": {
                    "type": "string",
                    "enum": ["count", "mean"],
                    "description": "Si se indica, devuelve un resumen en vez de filas.",
                },
                "limite": {
                    "type": "integer",
                    "description": "Máximo de filas a devolver sin agregación. Por defecto 20.",
                },
            },
        },
    },
]

FUNCIONES = {
    "consultar_datos": consultar_datos,
}

cliente = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def ejecutar_herramienta(nombre: str, argumentos: dict) -> str:
    """Ejecuta la función Python asociada y devuelve el resultado como texto."""
    try:
        resultado = FUNCIONES[nombre](**argumentos)
    except Exception as e:
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
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=HERRAMIENTAS,
            messages=mensajes,
        )
        mensajes.append({"role": "assistant", "content": respuesta.content})

        if respuesta.stop_reason != "tool_use":
            texto = "".join(b.text for b in respuesta.content if b.type == "text")
            return texto, mensajes

        resultados = []
        for bloque in respuesta.content:
            if bloque.type == "tool_use":
                salida = ejecutar_herramienta(bloque.name, bloque.input)
                resultados.append(
                    {"type": "tool_result", "tool_use_id": bloque.id, "content": salida}
                )
        mensajes.append({"role": "user", "content": resultados})


if __name__ == "__main__":
    import sys

    pregunta = " ".join(sys.argv[1:]) or "¿Cuántos clientes tienen pension_plan?"
    texto, _ = responder(pregunta)
    print(texto)