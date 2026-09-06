"""Segmento de cliente según el clustering de la Tarea 3."""

from functools import lru_cache
from pathlib import Path

import pandas as pd

RUTA_GRUPOS = Path(__file__).resolve().parent.parent / "data" / "clientes_grupos.csv"

PERFILES = {
    "Sin producto": {
        "descripcion": "Se registraron pero nunca contrataron nada. No son clientes todavía.",
        "accion": "Activación: campaña para que contraten su primer producto, empezando por la cuenta básica.",
    },
    "Universitarios inactivos": {
        "descripcion": "Jóvenes de unos 24 años con solo la cuenta básica desde antes de 2018 y ninguna contratación en 17 meses. Solo uno de cada cuatro entra en la app.",
        "accion": "Reactivación: recuperar el uso de la app antes de intentar vender nada. Prioridad baja en presupuesto.",
    },
    "Universitarios recién llegados": {
        "descripcion": "Mismo perfil que los inactivos, pero abrieron la cuenta hace menos de un año. La mitad usa la app.",
        "accion": "Acompañamiento: consolidar el hábito en los primeros meses; tarjeta de débito como segundo producto.",
    },
    "Particulares básicos": {
        "descripcion": "Adultos de unos 43 años con la cuenta y poco más. Activos, pero con una relación mínima con la entidad.",
        "accion": "Segundo producto: tarjeta de débito y cuenta nómina como puerta de entrada.",
    },
    "Particulares con tarjeta": {
        "descripcion": "Adultos de unos 41 años con cuenta y tarjeta de débito, casi todos activos. Ya han demostrado que compran.",
        "accion": "Nómina: el paso natural es domiciliar la nómina, que es lo que separa a este grupo del de mayor margen.",
    },
    "Clientes de nómina": {
        "descripcion": "Entraron por la cuenta nómina, unos 35 años, muy activos y con un margen 25 veces mayor que el particular básico.",
        "accion": "Plan de pensiones: tienen la nómina pero no el plan. El perfil donde el modelo de propensión de pension_plan es más útil.",
    },
    "Nómina y pensiones": {
        "descripcion": "Los clientes más vinculados: nómina, cuenta nómina, plan de pensiones y cuatro productos de media. El margen más alto de todos.",
        "accion": "Fidelización: el objetivo no es venderles más, es que no se vayan. Inversión y ahorro a largo plazo como complemento.",
    },
    "TOP ahorradores": {
        "descripcion": "Clientes de unos 55 años del segmento TOP, con la renta más alta y depósitos a largo plazo. Pocos, pero de alto valor.",
        "accion": "Asesoramiento: productos de inversión y ahorro a largo plazo.",
    },
}


@lru_cache(maxsize=1)
def _cargar_grupos() -> pd.DataFrame:
    """Lee la tabla de grupos una sola vez, indexada por cliente."""
    return pd.read_csv(RUTA_GRUPOS).set_index("pk_cid")


def obtener_segmento(cliente_id: int) -> dict:
    """Devuelve el grupo al que pertenece un cliente según la segmentación.

    Args:
        cliente_id: Identificador del cliente (cid).

    Returns:
        Diccionario con cuatro claves:
        - "cliente_id": el identificador consultado.
        - "grupo": nombre del grupo asignado por el clustering.
        - "descripcion": perfil del grupo.
        - "accion": estrategia comercial recomendada para ese grupo.
        Si el cliente no existe en la segmentación, "grupo" es None y las
        otras dos claves quedan vacías.
    """
    df = _cargar_grupos()
    cliente_id = int(cliente_id)

    if cliente_id not in df.index:
        return {"cliente_id": cliente_id, "grupo": None, "descripcion": "", "accion": ""}

    nombre = df.loc[cliente_id, "nombre_grupo"]
    perfil = PERFILES.get(nombre, {"descripcion": "", "accion": ""})
    return {
        "cliente_id": cliente_id,
        "grupo": nombre,
        "descripcion": perfil["descripcion"],
        "accion": perfil["accion"],
    }