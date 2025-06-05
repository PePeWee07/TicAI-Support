function_registry: dict[str, dict] = {}

def register_function(func_id: str):
    """
    Decorador que registra la función bajo func_id
    y crea la clave "allowed_roles" como set vacío.
    """
    def decorator(func):
        function_registry[func_id] = {
            "func": func,
            "allowed_roles": set()  # inicialmente nadie tiene permiso
        }
        return func
    return decorator

def requires_roles(func_id: str, roles: list[str]):
    """
    Decorador que, dado un func_id ya registrado, asigna la lista de roles
    (en MAYÚSCULAS) que tienen permiso para invocar esa función.
    """
    def decorator(func):
        entry = function_registry.get(func_id)
        if entry is None:
            raise RuntimeError(
                f"Tried to assign roles to '{func_id}' before registering it."
            )
        entry["allowed_roles"] = {r.strip().upper() for r in roles}
        return func
    return decorator
