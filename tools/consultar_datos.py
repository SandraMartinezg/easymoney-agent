"""Consulta sobre las tablas de clientes y ventas: filtrado, selección de columnas y agregación."""

from functools import lru_cache
from pathlib import Path

import pandas as pd

RUTA_DATA = Path(__file__).resolve().parent.parent / "data"
TABLAS = ["clientes", "ventas"]


def _compactar(df: pd.DataFrame) -> pd.DataFrame:
    """Reduce memoria: textos repetidos como categoría y números en 32 bits."""
    for columna in df.columns:
        if df[columna].dtype == object or pd.api.types.is_string_dtype(df[columna]):
            df[columna] = df[columna].astype("category")
        elif pd.api.types.is_float_dtype(df[columna]):
            df[columna] = df[columna].astype("float32")
        elif pd.api.types.is_integer_dtype(df[columna]):
            df[columna] = pd.to_numeric(df[columna], downcast="integer")
    return df


@lru_cache(maxsize=2)
def _cargar_tabla(tabla: str) -> pd.DataFrame:
    """Lee una tabla una sola vez, compactada, y la mantiene en memoria."""
    if tabla == "clientes":
        df = pd.read_csv(RUTA_DATA / "clientes.csv").rename(columns={"pk_cid": "cid"})
    else:
        df = pd.read_csv(RUTA_DATA / "df_powerbi.csv", sep=";", decimal=",")
    return _compactar(df)


def _cargar_datos() -> pd.DataFrame:
    """Compatibilidad: la tabla de ventas."""
    return _cargar_tabla("ventas")


def consultar_datos(
    tabla: str = "clientes",
    filtros: dict | None = None,
    columnas: list[str] | None = None,
    agregacion: str | None = None,
    agrupar_por: str | None = None,
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
            Valores admitidos: "count" (número de filas), "mean" (media de
            las columnas numéricas indicadas en `columnas`) o "sum" (suma).
        agrupar_por: Columna por la que agrupar la agregación. Ejemplo:
            agregacion="count", agrupar_por="product_desc" devuelve el
            número de filas por producto, ordenado de mayor a menor.
        limite: Número máximo de filas (o de grupos) a devolver.

    Returns:
        Diccionario con tres claves:
        - "tabla": la tabla consultada.
        - "n_filas": número de filas que cumplen los filtros.
        - "resultado": lista de registros (dict por fila), un dict con el
          valor agregado, o una lista de dicts (uno por grupo) si se agrupa.
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

    if agrupar_por and agrupar_por not in df.columns:
        raise ValueError(f"La columna '{agrupar_por}' no existe en la tabla '{tabla}'.")

    if columnas:
        inexistentes = [c for c in columnas if c not in df.columns]
        if inexistentes:
            raise ValueError(f"Columnas inexistentes en '{tabla}': {inexistentes}")
        if agrupar_por and agrupar_por not in columnas:
            columnas = columnas + [agrupar_por]
        df = df[columnas]

    n_filas = len(df)

    if agregacion is not None and agregacion not in ("count", "mean", "sum"):
        raise ValueError(f"Agregación no admitida: '{agregacion}'. Usa 'count', 'mean' o 'sum'.")

    if agregacion and agrupar_por:
        grupos = df.groupby(agrupar_por, observed=True)
        numericas = [c for c in df.select_dtypes("number").columns if c != agrupar_por]
        if agregacion == "count":
            resumen = grupos.size().rename("count").to_frame()
        elif agregacion == "mean":
            resumen = grupos[numericas].mean().round(2)
        else:
            resumen = grupos[numericas].sum().round(2)
        resumen = resumen.sort_values(resumen.columns[0], ascending=False).head(limite)
        return {"tabla": tabla, "n_filas": n_filas, "resultado": resumen.reset_index().to_dict(orient="records")}

    if agregacion == "count":
        return {"tabla": tabla, "n_filas": n_filas, "resultado": {"count": n_filas}}

    if agregacion == "mean":
        medias = df.select_dtypes("number").mean().round(2)
        return {"tabla": tabla, "n_filas": n_filas, "resultado": medias.to_dict()}

    if agregacion == "sum":
        sumas = df.select_dtypes("number").sum().round(2)
        return {"tabla": tabla, "n_filas": n_filas, "resultado": sumas.to_dict()}

    filas = df.head(limite).astype(object).where(pd.notna(df.head(limite)), None)
    return {"tabla": tabla, "n_filas": n_filas, "resultado": filas.to_dict(orient="records")}