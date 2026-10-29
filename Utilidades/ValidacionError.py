# ---------------------------------------------------------
# UTILIDADES/ValidacionError.py
# ---------------------------------------------------------

class ValidacionError(Exception):
    """Error de dominio: los datos ingresados no son válidos para el cálculo.

    La interfaz lo captura para mostrar `mensaje` al usuario, sin confundirlo
    con errores inesperados (bugs) del programa.
    """

    def __init__(self, mensaje: str) -> None:
        super().__init__(mensaje)
        self.mensaje = mensaje