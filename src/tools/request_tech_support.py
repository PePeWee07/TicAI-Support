from tools.registry import register_function, requires_roles

@requires_roles("request_tech_support", ["ADMINISTRATIVO"])
@register_function("request_tech_support")
def request_tech_support(**kwargs):
    return "El soporte técnico ha sido solicitado con éxito. Esta en camino."