"""Lista priorizada de contactos según la estrategia de campaña de la Tarea 4."""

from tools.predecir_propension import PRODUCTOS_DISPONIBLES, _cargar_scoring

NUCLEO = ["Clientes de nómina", "Particulares con tarjeta"]
EXCLUIR = ["Universitarios inactivos", "Sin producto", "Sin grupo"]


def recomendar_contactos(
    producto: str = "pension_plan",
    n: int = 20,
    top_resto_pct: int = 20,
) -> dict:
    """Devuelve los clientes a contactar aplicando la estrategia híbrida.

    Regla (estrategia D de la Tarea 4): se contacta a todos los clientes de
    los grupos núcleo y, del resto de grupos, solo al top `top_resto_pct` %
    por probabilidad. Los grupos excluidos no se contactan nunca.

    Args:
        producto: "pension_plan" (campaña recomendada) o "em_acount".
        n: Número de clientes a devolver, ordenados por probabilidad.
        top_resto_pct: Porcentaje del modelo que se contacta fuera del núcleo.
            Por defecto 20, el valor que la Tarea 4 identificó como óptimo.

    Returns:
        Diccionario con cuatro claves:
        - "producto" y "regla": lo aplicado, en texto.
        - "n_recomendados": total de clientes que cumplen la regla.
        - "contactos": lista de dicts con "cliente_id", "probabilidad",
          "grupo" y "motivo" ("grupo núcleo" o "top del modelo"), ordenada
          de mayor a menor probabilidad y limitada a `n`.
    """
    if producto not in PRODUCTOS_DISPONIBLES:
        raise ValueError(
            f"No hay scoring para '{producto}'. Disponibles: {PRODUCTOS_DISPONIBLES}."
        )

    df = _cargar_scoring(producto).copy()
    col_prob = f"probabilidad_{producto}"
    df["nombre_grupo"] = df["nombre_grupo"].fillna("Sin grupo")

    umbral = df[col_prob].quantile(1 - top_resto_pct / 100)
    en_nucleo = df["nombre_grupo"].isin(NUCLEO)
    en_resto = ~df["nombre_grupo"].isin(NUCLEO + EXCLUIR) & (df[col_prob] >= umbral)

    seleccion = df[en_nucleo | en_resto].copy()
    seleccion["motivo"] = "top del modelo"
    seleccion.loc[seleccion["nombre_grupo"].isin(NUCLEO), "motivo"] = "grupo núcleo"
    seleccion = seleccion.sort_values(col_prob, ascending=False)

    contactos = [
        {
            "cliente_id": int(fila["pk_cid"]),
            "probabilidad": round(float(fila[col_prob]), 4),
            "grupo": fila["nombre_grupo"],
            "motivo": fila["motivo"],
        }
        for _, fila in seleccion.head(n).iterrows()
    ]

    return {
        "producto": producto,
        "regla": (
            f"Grupos núcleo completos ({', '.join(NUCLEO)}) más el top {top_resto_pct}% "
            f"del modelo en el resto de grupos; excluidos: {', '.join(EXCLUIR)}."
        ),
        "n_recomendados": len(seleccion),
        "contactos": contactos,
    }