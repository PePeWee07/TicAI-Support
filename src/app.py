from flask import Flask, request, jsonify
import services.openai_service as openai_service
from services.utils import moderation_required, validate_token_limit
from config.logging_config import logger
import os
import atexit
from tools.loader import load_tools_from_folder

app = Flask(__name__)

ENV_MODE = os.getenv("FLASK_ENV", "production")

logger.info("Servicio Iniciado...")

# ==================================================
# Cargar funciones de herramientas
# ==================================================
load_tools_from_folder("src/tools")


# ==================================================
# Verificar si se ha configurado el token de OpenAI
# ==================================================
API_KEY = os.getenv("API_KEY")
def require_api_key(f):
    def wrapper(*args, **kwargs):
        api_key = request.headers.get('Authorization')
        if api_key != f"Bearer {API_KEY}":
            return jsonify({"msg": "Unauthorized"}), 401
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__  
    return wrapper

# ==================================================
# Inicializar el asistente
# ==================================================
assistant = openai_service.verify_assistant()
    
    
# ==================================================
# Ruta para preguntar al asistente
# ==================================================
@app.route('/ask', methods=['POST'])
@moderation_required
@validate_token_limit
@require_api_key
def process_user_input():
    if assistant is None:
        return jsonify({"error": "El asistente no está disponible debido a un error."}), 500

    data = request.json
    ask = data.get('ask')
    name = data.get('name')
    phone = data.get('phone')
    thread_id = data.get('thread_id')

    if not ask:
        return jsonify({"error": "Se requiere una pregunta."}), 400
    if not name:
        return jsonify({"error": "Se requiere un nombre."}), 400

    try:
        answer, thread_id = openai_service.get_response(assistant.id, ask, name, phone, thread_id)
        return jsonify({"answer": answer, "thread_id": thread_id}), 200
    except ValueError as e:
        logger.error(f"Error al obtener respuesta: {e}")
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.error(f"Error inesperado al obtener respuesta: {e}")
        return jsonify({"error": str(e)}), 500


# ==================================================
# Obtener el historial de mensajes de un hilo
# ==================================================
@app.route('/history', methods=['GET'])
@require_api_key
def get_history():
    thread_id = request.args.get('thread_id')

    if not thread_id:
        return jsonify({"error": "Se requiere un thread_id."}), 400

    try:
        history = openai_service.view_history(thread_id)
        return jsonify({"history": history}), 200
    except ValueError as e:
        logger.error(f"Error al obtener historial: {e}")
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.error(f"Error inesperado al obtener historial: {e}")
        return jsonify({"error": str(e)}), 500


# ==================================================
# Eliminar un hilo
# ==================================================
@app.route('/delete-thread-id', methods=['DELETE'])
@require_api_key
def delete_thread_endpoint():
    thread_id = request.args.get('thread_id')

    if not thread_id:
        return jsonify({"error": "Se requiere un thread_id."}), 400

    try:
        message = openai_service.delete_thread(thread_id)
        return jsonify({"message": message}), 200
    except ValueError as e:
        logger.error(f"Error al eliminar hilo: {e}")
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.error(f"Error inesperado al eliminar hilo: {e}")
        return jsonify({"error": str(e)}), 500


# ==================================================
# Eliminar multiples hilos
# ==================================================
@app.route('/delete-threads-ids', methods=['DELETE'])
@require_api_key
def delete_threads_endpoint():
    data = request.get_json()
    if not data or 'ids' not in data:
        return jsonify({"error": "Se requiere una lista de IDs de hilos en el campo 'ids'."}), 400

    ids = data['ids']
    if not isinstance(ids, list) or not all(isinstance(i, str) for i in ids):
        return jsonify({"error": "El campo 'ids' debe ser una lista de strings."}), 400

    try:
        message = openai_service.delete_threads(ids)
        logger.info(f"Hilos eliminados: {message}")
        return jsonify({"message": message}), 200
    except TypeError as e:
        logger.error(f"Error al eliminar hilos: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error inesperado al eliminar hilos: {e}")
        return jsonify({"error": {e}}), 500


# ==================================================
# Cerrar recursos al salir
# ==================================================
def clean_up():
    logger.info("Cerrando aplicación y limpiando recursos.") 
atexit.register(clean_up)


if __name__ == '__main__':
    if ENV_MODE == "development":
        print("🚀 Modo Desarrollo: Activando Flask Debug Server con Hot Reload")
        app.run(
            host="0.0.0.0", 
            port=5000, 
            debug=False,
            threaded=True
        )
    else:
        print("🚀 Modo Producción: Usando Gunicorn")