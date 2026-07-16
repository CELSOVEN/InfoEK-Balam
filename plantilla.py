def procesar_datos(datos):
    """
    Procesa los datos recibidos desde la aplicación web.

    Este método debe modificarse de acuerdo con la lógica
    específica de cada nuevo proyecto.

    Args:
        datos (dict): Datos recibidos desde el formulario HTML.

    Returns:
        dict: Resultado que será enviado nuevamente a la interfaz.
    """

    return {
        "mensaje": "Los datos fueron recibidos correctamente.",
        "datos_recibidos": datos
    }