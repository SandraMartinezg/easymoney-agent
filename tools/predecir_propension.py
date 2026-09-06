"""Predicción de propensión de compra con el modelo de la Tarea 2."""

from functools import lru_cache
from pathlib import Path

import pandas as pd

RUTA_DATA = Path(__file__).resolve().parent.parent / "data"
PRODUCTOS_DISPONIBLES = ["pension_plan", "em_acount"]


@lru_cache(maxsize=2)
def _cargar_scoring(producto: str) -> pd.DataFrame:
    """Lee la tabla de scoring de un producto una sola vez."""
    return pd.read_csv(RUTA_DATA / f"scoring_grupo_{producto}.csv")


def predecir_propension(
    producto: str,
    cliente_id: int | None = None,
    top_n: int = 10,
) -> dict:
    """Devuelve la probabilidad de que un cliente contrate un producto.

    Solo hay modelo para los productos de PRODUCTOS_DISPONIBLES. La tabla de
    scoring contiene únicamente clientes elegibles: los que aún no tienen el
    producto.

    Args:
        producto: "pension_plan" o "em_acount".
        cliente_id: Identificador del cliente (cid). Si se indica, se devuelve
            solo su predicción. Si es None, se devuelven los `top_n` clientes
            con mayor probabilidad.
        top_n: Número de clientes a devolver cuando cliente_id es None.

    Returns:
        Diccionario con tres claves:
        - "producto": el producto consultado.
        - "n_elegibles": número total de clientes puntuados.
        - "predicciones": lista de dicts con "cliente_id", "probabilidad"
          (float entre 0 y 1) y "grupo", ordenada de mayor a menor
          probabilidad. Si se indicó cliente_id y no está entre los
          elegibles, la lista queda vacía.
    """
    if producto not in PRODUCTOS_DISPONIBLES:
        raise ValueError(
            f"No hay modelo de propensión para '{producto}'. "
            f"Productos disponibles: {PRODUCTOS_DISPONIBLES}."
        )

    df = _cargar_scoring(producto)
    col_prob = f"probabilidad_{producto}"

    if cliente_id is not None:
        seleccion = df[df["pk_cid"] == int(cliente_id)]
    else:
        seleccion = df.nlargest(top_n, col_prob)

    predicciones = [
        {
            "cliente_id": int(fila["pk_cid"]),
            "probabilidad": round(float(fila[col_prob]), 4),
            "grupo": fila["nombre_grupo"],
        }
        for _, fila in seleccion.iterrows()
    ]

    return {"producto": producto, "n_elegibles": len(df), "predicciones": predicciones}