# Diccionario para almacenar las funciones registradas.
function_registry = {}

def register_function(func_id):
    """
    Decorador para registrar una función con un identificador único.
    """
    def decorator(func):
        function_registry[func_id] = func
        return func
    return decorator
