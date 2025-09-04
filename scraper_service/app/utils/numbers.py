def get_float(text: str) -> float:
    """
    Obtiene un valor float de un texto.

    Args:
        text (str): El texto a convertir.

    Returns:
        float: El valor float obtenido o 0.0 si no es posible convertir.
    """
    try:
        return float(text)
    except ValueError:
        return 0.0


def get_integer(text: str) -> int:
    """
    Obtiene un valor entero de un texto.

    Args:
        text (str): El texto a convertir.

    Returns:
        int: El valor entero obtenido o 0 si no es posible convertir.
    """
    try:
        return int(text)
    except ValueError:
        return 0
