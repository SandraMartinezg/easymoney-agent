"""Explicación de una predicción de propensión mediante SHAP."""


def explicar_prediccion(
    cliente_id: int,
    producto: str,
    top_variables: int = 5,
) -> dict:
    """Explica qué variables empujan la predicción de un cliente.

    Args:
        cliente_id: Identificador del cliente (cid).
        producto: Producto cuya predicción se explica, por ejemplo
            "pension_plan" o "em_acount".
        top_variables: Número de variables a devolver, ordenadas por
            impacto absoluto.

    Returns:
        Diccionario con tres claves:
        - "cliente_id" y "producto": lo consultado.
        - "variables": lista de dicts con "nombre", "valor" (valor de la
          variable para ese cliente) e "impacto" (valor SHAP; positivo
          aumenta la probabilidad, negativo la reduce), ordenada por
          impacto absoluto descendente.
    """
    raise NotImplementedError