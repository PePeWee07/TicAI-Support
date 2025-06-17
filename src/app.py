from flask import Flask, request, jsonify
import services.openAIService as openAIService
from services.utils import moderation_required, validate_token_limit
from config.logging_config import logger
import os
import atexit
from tools.config.loader import load_tools_from_folder
import datetime
import pytz
from flask_cors import CORS
from models.userData import UserData
from pydantic import ValidationError

app = Flask(__name__)
# CORS(app, resources={r"/ia/health": {"origins": ["https://ia-sp-webhook.ucatolica.cue.ec", "https://ia-sp-backoffice.ucatolica.cue.ec"]}})
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True, allow_headers=["Authorization", "Content-Type"])

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
assistant = openAIService.verify_assistant()
    
    
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

    try:
        user = UserData(**request.json)

    except ValidationError as ve:
        return jsonify({"error": ve.errors()}), 400

    try:
        answer, new_thread_id = openAIService.get_response(assistant.id, user)
        return jsonify({"answer": answer, "thread_id": new_thread_id}), 200

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
        history = openAIService.view_history(thread_id)
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
        message = openAIService.delete_thread(thread_id)
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
        message = openAIService.delete_threads(ids)
        logger.info(f"Hilos eliminados: {message}")
        return jsonify({"message": message}), 200
    except TypeError as e:
        logger.error(f"Error al eliminar hilos: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error inesperado al eliminar hilos: {e}")
        return jsonify({"error": {e}}), 500


# ==================================================
# Healthcheck
# ==================================================
@app.route('/health', methods=['GET'])
def health_check():
    now_date = datetime.datetime.now(pytz.timezone('America/Guayaquil'))
    formatted_time = now_date.strftime('%-m/%-d/%Y, %-I:%M:%S %p')
    return jsonify({
        "status": "ok",
        "message": "API is running.",
        "timestamp": formatted_time
    }), 200
    

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