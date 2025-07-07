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
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True, allow_headers=["Authorization", "Content-Type"])

ENV_MODE = os.getenv("FLASK_ENV", "production")
API_KEY = os.getenv("API_KEY")

if not API_KEY :
    logger.error("LA 'API_KEY' para el back-end no está configurado en las variables de entorno.")
    raise ValueError("LA 'API_KEY' para el back-end no está configurado en las variables de entorno.")

logger.info("Servicio Iniciado...")

# =========== Load tools Functions ================
load_tools_from_folder("src/tools")


# =========== Verify Token API_KEY =================
def require_api_key(f):
    def wrapper(*args, **kwargs):
        api_key = request.headers.get('Authorization')
        if api_key != f"Bearer {API_KEY}":
            return jsonify({"msg": "Unauthorized"}), 401
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__  
    return wrapper
    
    
# =========== Input of user ==================
@app.route('/ask', methods=['POST'])
@moderation_required
@validate_token_limit
@require_api_key
def process_user_input():
    try:
        user = UserData(**request.json)

        answer, response_id = openAIService.get_response(user)
        return jsonify({"answer": answer, "previousResponseId": response_id}), 200
    
    except ValidationError as ve:
        logger.error(f"error: {ve}")
        return jsonify({"error": ve.errors()}), 400

    except ValueError as e:
        logger.error(f"Error al obtener respuesta: {e}")
        return jsonify({"error": str(e)}), 404

    except Exception as e:
        logger.error(f"Error inesperado al obtener respuesta: {e}")
        return jsonify({"error": str(e)}), 500


# ==================================================
# TODO: Historial
# ==================================================


# ============ Healthcheck =======================
@app.route('/health', methods=['GET'])
def health_check():
    now_date = datetime.datetime.now(pytz.timezone('America/Guayaquil'))
    formatted_time = now_date.strftime('%-m/%-d/%Y, %-I:%M:%S %p')
    return jsonify({
        "status": "ok",
        "message": "API is running.",
        "timestamp": formatted_time
    }), 200
    

# ============ Cerrar recursos al salir ==================
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