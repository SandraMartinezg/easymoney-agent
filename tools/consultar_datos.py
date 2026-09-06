"""Consulta sobre las tablas de clientes y ventas: filtrado, selección de columnas y agregación."""

from functools import lru_cache
from pathlib import Path

import pandas as pd

RUTA_DATA = Path(__file__).resolve().parent.parent / "data"
TABLAS = ["clientes", "ventas"]


@lru_cache(maxsize=2)
def _cargar_tabla(tabla: str) -> pd.DataFrame:
    """Lee una tabla una sola vez y la mantiene en memoria."""
    if tabla == "clientes":
        return pd.read_csv(RUTA_DATA / "clientes.csv").rename(columns={"pk_cid": "cid"})
    return pd.read_csv(RUTA_DATA / "df_powerbi.csv", sep=";", decimal=",")


def _cargar_datos() -> pd.DataFrame:
    """Compatibilidad: la tabla de ventas."""
    return _cargar_tabla("ventas")


def consultar_datos(
    tabla: str = "clientes",
    filtros: dict | None = None,
    columnas: list[str] | None = None,
    agregacion: str | None = None,
    limite: int = 20,
) -> dict:
    """Filtra y resume una tabla de easyMoney.

    Args:
        tabla: "clientes" (una fila por cliente, foto a mayo de 2019, con
            datos sociodemográficos, actividad y productos 0/1) o "ventas"
            (una fila por venta 2018-2019, con margen y producto vendido).
        filtros: Condiciones de igualdad columna -> valor. Ejemplo:
            {"pension_plan": 1, "segment": "03 - UNIVERSITARIO"}.
            Si es None, no se filtra.
        columnas: Columnas a devolver. Si es None, se devuelven todas.
        agregacion: Si se indica, en lugar de filas devuelve un resumen.
            Valores admitidos: "count" (número de filas) o "mean"
            (media de las columnas numéricas indicadas en `columnas`).
        limite: Número máximo de filas a devolver cuando no hay agregación.

    Returns:
        Diccionario con tres claves:
        - "tabla": la tabla consultada.
        - "n_filas": número de filas que cumplen los filtros.
        - "resultado": lista de registros (dict por fila) o, si hay
          agregación, un dict con el valor agregado.
    """
    if tabla not in TABLAS:
        raise ValueError(f"Tabla '{tabla}' no existe. Usa una de {TABLAS}.")

    df = _cargar_tabla(tabla)

    if filtros:
        for columna, valor in filtros.items():
            if columna not in df.columns:
                raise ValueError(f"La columna '{columna}' no existe en la tabla '{tabla}'.")
            if pd.api.types.is_numeric_dtype(df[columna]) and isinstance(valor, str):
                valor = float(valor)
            df = df[df[columna] == valor]

    if columnas:
        inexistentes = [c for c in columnas if c not in df.columns]
        if inexistentes:
            raise ValueError(f"Columnas inexistentes en '{tabla}': {inexistentes}")
        df = df[columnas]

    n_filas = len(df)

    if agregacion == "count":
        return {"tabla": tabla, "n_filas": n_filas, "resultado": {"count": n_filas}}

    if agregacion == "mean":
        medias = df.select_dtypes("number").mean().round(2)
        return {"tabla": tabla, "n_filas": n_filas, "resultado": medias.to_dict()}

    if agregacion is not None:
        raise ValueError(f"Agregación no admitida: '{agregacion}'. Usa 'count' o 'mean'.")

    filas = df.head(limite).astype(object).where(pd.notna(df.head(limite)), None)
    return {"tabla": tabla, "n_filas": n_filas, "resultado": filas.to_dict(orient="records")}