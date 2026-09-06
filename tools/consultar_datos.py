"""Consulta sobre df_powerbi.csv: filtrado, selección de columnas y agregación."""

import pandas as pd


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
    raise NotImplementedError