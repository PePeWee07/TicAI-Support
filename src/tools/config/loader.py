import os
import importlib

def load_tools_from_folder(folder_path):
    """
    Carga dinámicamente todos los archivos .py en la carpeta especificada
    (excepto __init__.py) para registrar las herramientas.
    """
    for filename in os.listdir(folder_path):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = filename[:-3]  # quitar extensión .py
            importlib.import_module(f"src.tools.{module_name}")
