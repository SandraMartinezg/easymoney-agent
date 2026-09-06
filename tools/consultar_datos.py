"""Consulta sobre df_powerbi.csv: filtrado, selección de columnas y agregación."""

from functools import lru_cache
from pathlib import Path

import pandas as pd

RUTA_DATOS = Path(__file__).resolve().parent.parent / "data" / "df_powerbi.csv"


@lru_cache(maxsize=1)
def _cargar_datos() -> pd.DataFrame:
    """Lee el CSV una sola vez y lo mantiene en memoria."""
    return pd.read_csv(RUTA_DATOS, sep=";", decimal=",")


def consultar_datos(
    filtros: dict | None = None,
    columnas: list[str] | None = None,
    agregacion: str | None = None,
    limite: int = 20,
) -> dict:
    """Filtra y resume el dataset de clientes de easyMoney.

    Args:
        filtros: Condiciones de igualdad columna -> valor. Ejemplo:
            {"pension_plan": 1, "segment": "03 - UNIVERSITARIO"}.
            Si es None, no se filtra.
        columnas: Columnas a devolver. Si es None, se devuelven todas.
        agregacion: Si se indica, en lugar de filas devuelve un resumen.
            Valores admitidos: "count" (número de filas) o "mean"
            (media de las columnas numéricas indicadas en `columnas`).
        limite: Número máximo de filas a devolver cuando no hay agregación.

    Returns:
        Diccionario con dos claves:
        - "n_filas": número de filas que cumplen los filtros.
        - "resultado": lista de registros (dict por fila) o, si hay
          agregación, un dict con el valor agregado.
    """
    df = _cargar_datos()

    if filtros:
        for columna, valor in filtros.items():
            if columna not in df.columns:
                raise ValueError(f"La columna '{columna}' no existe en el dataset.")
            if pd.api.types.is_numeric_dtype(df[columna]) and isinstance(valor, str):
                valor = float(valor)
            df = df[df[columna] == valor]

    if columnas:
        inexistentes = [c for c in columnas if c not in df.columns]
        if inexistentes:
            raise ValueError(f"Columnas inexistentes: {inexistentes}")
        df = df[columnas]

    n_filas = len(df)

    if agregacion == "count":
        return {"n_filas": n_filas, "resultado": {"count": n_filas}}

    if agregacion == "mean":
        medias = df.select_dtypes("number").mean().round(2)
        return {"n_filas": n_filas, "resultado": medias.to_dict()}

    if agregacion is not None:
        raise ValueError(f"Agregación no admitida: '{agregacion}'. Usa 'count' o 'mean'.")

    return {"n_filas": n_filas, "resultado": df.head(limite).to_dict(orient="records")}