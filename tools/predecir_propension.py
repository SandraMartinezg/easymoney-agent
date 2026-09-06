"""Predicción de propensión de compra con el modelo de la Tarea 2."""


def predecir_propension(
    producto: str,
    cliente_id: int | None = None,
    top_n: int = 10,
) -> dict:
    """Devuelve la probabilidad de que un cliente contrate un producto.

    Args:
        producto: Producto a predecir. Debe ser una de las columnas de
            producto del dataset, por ejemplo "pension_plan", "credit_card",
            "loans" o "em_acount".
        cliente_id: Identificador del cliente (cid). Si se indica, se
            devuelve solo la predicción de ese cliente. Si es None, se
            puntúan todos los clientes que aún no tienen el producto y se
            devuelven los `top_n` con mayor probabilidad.
        top_n: Número de clientes a devolver cuando cliente_id es None.

    Returns:
        Diccionario con dos claves:
        - "producto": el producto consultado.
        - "predicciones": lista de dicts con "cliente_id" y "probabilidad"
          (float entre 0 y 1), ordenada de mayor a menor probabilidad.
          Si se indicó cliente_id, la lista tiene un solo elemento.
    """
    raise NotImplementedError