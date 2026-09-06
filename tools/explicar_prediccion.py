"""Explicación de una predicción de propensión mediante SHAP."""

import warnings
from functools import lru_cache
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import shap
from sklearn.exceptions import InconsistentVersionWarning

RUTA_BASE = Path(__file__).resolve().parent.parent
PRODUCTOS_EXPLICABLES = ["pension_plan"]


@lru_cache(maxsize=1)
def _cargar_modelo(producto: str):
    """Carga el modelo y construye el explicador SHAP una sola vez."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", InconsistentVersionWarning)
        modelo = joblib.load(RUTA_BASE / "models" / f"modelo_{producto}.joblib")
    return modelo, shap.TreeExplainer(modelo)


@lru_cache(maxsize=1)
def _cargar_matriz(producto: str) -> pd.DataFrame:
    """Matriz de variables de los clientes elegibles, tal como la ve el modelo."""
    return pd.read_parquet(RUTA_BASE / "data" / f"X_scoring_{producto}.parquet")


def _nombre_legible(columna: str) -> str:
    """Convierte 'salary_lag1' en 'salary' y 'segment_lag1_01 - TOP' en 'segment = 01 - TOP'."""
    columna = columna.replace("_lag1", "")
    for prefijo in ("gender", "segment", "entry_channel", "region_code", "mes"):
        if columna.startswith(prefijo + "_"):
            return f"{prefijo} = {columna[len(prefijo) + 1:]}"
    return columna


def explicar_prediccion(
    cliente_id: int,
    producto: str = "pension_plan",
    top_variables: int = 5,
) -> dict:
    """Explica qué variables empujan la predicción de un cliente.

    Args:
        cliente_id: Identificador del cliente (cid).
        producto: Producto cuya predicción se explica. Solo "pension_plan".
        top_variables: Número de variables a devolver, ordenadas por
            impacto absoluto.

    Returns:
        Diccionario con cuatro claves:
        - "cliente_id" y "producto": lo consultado.
        - "probabilidad": la probabilidad predicha por el modelo.
        - "variables": lista de dicts con "nombre", "valor" (valor de la
          variable para ese cliente) e "impacto" (valor SHAP; positivo
          aumenta la probabilidad, negativo la reduce), ordenada por
          impacto absoluto descendente.
        Si el cliente no está entre los elegibles, "variables" queda vacía.
    """
    if producto not in PRODUCTOS_EXPLICABLES:
        raise ValueError(
            f"No hay explicaciones para '{producto}'. Disponibles: {PRODUCTOS_EXPLICABLES}."
        )

    X = _cargar_matriz(producto)
    cliente_id = int(cliente_id)
    if cliente_id not in X.index:
        return {"cliente_id": cliente_id, "producto": producto, "probabilidad": None, "variables": []}

    modelo, explicador = _cargar_modelo(producto)
    fila = X.loc[[cliente_id]]
    probabilidad = float(modelo.predict_proba(fila)[0, 1])

    valores = explicador.shap_values(fila)
    if isinstance(valores, list):
        impactos = np.asarray(valores[1])[0]
    else:
        valores = np.asarray(valores)
        impactos = valores[0, :, 1] if valores.ndim == 3 else valores[0]

    contribuciones = pd.DataFrame({
        "nombre": [_nombre_legible(c) for c in fila.columns],
        "valor": fila.iloc[0].values,
        "impacto": impactos,
    })
    contribuciones = contribuciones[~((contribuciones["nombre"].str.contains(" = ")) & (contribuciones["valor"] == 0))]
    contribuciones = contribuciones.reindex(
        contribuciones["impacto"].abs().sort_values(ascending=False).index
    ).head(top_variables)

    return {
        "cliente_id": cliente_id,
        "producto": producto,
        "probabilidad": round(probabilidad, 4),
        "variables": [
            {
                "nombre": fila_c["nombre"],
                "valor": round(float(fila_c["valor"]), 2),
                "impacto": round(float(fila_c["impacto"]), 4),
            }
            for _, fila_c in contribuciones.iterrows()
        ],
    }