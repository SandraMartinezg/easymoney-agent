"""Construye data/clientes.csv: una fila por cliente con su última foto disponible.

Uso:
    python scripts/preparar_clientes.py RUTA_A_LA_CARPETA_RAW_DEL_TFM
"""

import sys
from pathlib import Path

import pandas as pd

RUTA_SALIDA = Path(__file__).resolve().parent.parent / "data" / "clientes.csv"


def ultima_foto(df: pd.DataFrame) -> pd.DataFrame:
    """Se queda con la partición más reciente de cada cliente."""
    return (
        df.sort_values("pk_partition")
        .drop_duplicates("pk_cid", keep="last")
        .drop(columns="pk_partition")
    )


def main(ruta_raw: str) -> None:
    raw = Path(ruta_raw)
    socio = pd.read_csv(raw / "customer_sociodemographics.csv", index_col=0)
    actividad = pd.read_csv(raw / "customer_commercial_activity.csv", index_col=0)
    productos = pd.read_csv(raw / "customer_products.csv", index_col=0)

    clientes = (
        ultima_foto(socio)
        .merge(ultima_foto(actividad), on="pk_cid", how="left")
        .merge(ultima_foto(productos), on="pk_cid", how="left")
    )

    columnas_producto = [c for c in productos.columns if c not in ("pk_cid", "pk_partition")]
    clientes[columnas_producto] = clientes[columnas_producto].fillna(0).astype(int)
    clientes["n_productos"] = clientes[columnas_producto].sum(axis=1)

    clientes.to_csv(RUTA_SALIDA, index=False)
    print(f"Guardado {RUTA_SALIDA}: {len(clientes):,} clientes, {clientes.shape[1]} columnas")
    print(list(clientes.columns))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])