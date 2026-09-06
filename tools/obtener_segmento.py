"""Segmento de cliente según el clustering de la Tarea 3."""


def obtener_segmento(cliente_id: int) -> dict:
    """Devuelve el grupo al que pertenece un cliente según la segmentación.

    Args:
        cliente_id: Identificador del cliente (cid).

    Returns:
        Diccionario con tres claves:
        - "cliente_id": el identificador consultado.
        - "grupo": etiqueta del grupo asignado por el clustering.
        - "descripcion": descripción breve del perfil del grupo, para que
          el agente pueda explicar qué caracteriza a ese cliente.
        Si el cliente no existe en la segmentación, "grupo" es None.
    """
    raise NotImplementedError